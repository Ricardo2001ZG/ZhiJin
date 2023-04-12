# fastbuild 学习笔记

---

# 简介

---

Fastbuild是一种针对传统构建系统性能问题而设计的快速构建系统。 它的核心思想是以高度并行化的方式构建项目，通过减少不必要的编译、链接和其他构建过程，来提高构建速度。这意味着减少了等待时间，从而使开发人员能够更快地进行测试和发布他们的应用程序。

Fastbuild是一个功能强大的构建系统，具有多种功能，包括增量编译、自动依赖关系分析、分布式编译、缓存编译结果等。这些功能使得Fastbuild可以更快地构建大型项目，同时也可以轻松地管理和构建小型项目。

此外，Fastbuild支持多种编译器和平台，并且易于配置和使用。这使得Fastbuild成为开发人员们首选的构建系统之一。无论你是一个个人开发者还是一个大型团队，Fastbuild都能够满足你的构建需求。

# 目录

---

# 内部组成部分

---

## `Tools\FBuild\FBuild\Main.cpp`

`Main` 函数的解析

```cpp
// Main
//------------------------------------------------------------------------------
int Main( int argc, char * argv[] )
{
		//代码调用 **PROFILE_FUNCTION** 宏，该宏可能在程序中用于性能剖析（profiling），也可能仅仅用于调试目的。
    PROFILE_FUNCTION;

    const Timer t;

    // Register Ctrl-C Handler
    CtrlCHandler ctrlCHandler;

    // 处理命令行参数
		// 行代码定义一个 **`FBuildOptions`** 对象 **`options`**，
		// 并设置一些属性。**`FBuildOptions`** 是一个类
		//用于处理程序的命令行参数（即 **`argc`** 和 **`argv`**）以及其他选项，如显示进度条、生成编译数据库等
    FBuildOptions options;
    options.m_SaveDBOnCompletion = true; // 覆盖默认值
    options.m_ShowProgress = true; // 覆盖默认值
    switch ( options.ProcessCommandLine( argc, argv ) )
    {
				// 如果返回 **`FBuildOptions::OPTIONS_OK`**，说明解析成功，程序可以继续执行。
        case FBuildOptions::OPTIONS_OK:             break;
				// 如果返回 **`FBuildOptions::OPTIONS_OK_AND_QUIT`**，说明解析成功，但程序不需要继续执行，可以直接退出。
        case FBuildOptions::OPTIONS_OK_AND_QUIT:    return FBUILD_OK;
				// 如果返回 **`FBuildOptions::OPTIONS_ERROR`**，说明解析失败，程序需要打印帮助信息并退出。
        case FBuildOptions::OPTIONS_ERROR:          return FBUILD_BAD_ARGS;
    }

    // 检查是否wrapper模式
    const FBuildOptions::WrapperMode wrapperMode = options.m_WrapperMode;

		// 程序是在一个中间进程（intermediate process）中运行的
		// 这种情况的处理被封装在 **`WrapperIntermediateProcess`** 函数中，程序调用该函数并返回其返回值。
    if ( wrapperMode == FBuildOptions::WRAPPER_MODE_INTERMEDIATE_PROCESS )
    {
        return WrapperIntermediateProcess( options );
    }

		// 说明程序是在 Windows 下的 Linux 子系统（Windows Subsystem for Linux, WSL）中运行的
		// 这种情况的处理被封装在 **`WrapperModeForWSL`** 函数中，程序调用该函数并返回其返回值。
    if ( wrapperMode == FBuildOptions::WRAPPER_MODE_WINDOWS_SUBSYSTEM_FOR_LINUX )
    {
        return WrapperModeForWSL( options );
    } 

    #if defined( __WINDOWS__ )
        // TODO:MAC Implement SetPriorityClass
        // TODO:LINUX Implement SetPriorityClass
				// 调用 **`SetPriorityClass`** 函数，将当前进程的优先级设置为 **`BELOW_NORMAL_PRIORITY_CLASS`**。
				// 该函数是 Windows 特有的 API，用于设置进程的优先级。这个调用可能会在其他操作系统上被省略。
        VERIFY( SetPriorityClass( GetCurrentProcess(), BELOW_NORMAL_PRIORITY_CLASS ) );
    #endif

    // 不使用缓冲
    VERIFY( setvbuf( stdout, nullptr, _IONBF, 0 ) == 0 );
    VERIFY( setvbuf( stderr, nullptr, _IONBF, 0 ) == 0 );

    // 确保只有一个Fastbuild实例在运行
    SystemMutex mainProcess( options.GetMainProcessMutexName().Get() );

    // 在“wrapper”模式下，Main进程使用此项监视最终进程的生命周期
    // （当主进程可以获得时，最终进程已终止）
    SystemMutex finalProcess( options.GetFinalProcessMutexName().Get() );

    // 同时只能运行一个实例
    if ( ( wrapperMode == FBuildOptions::WRAPPER_MODE_MAIN_PROCESS ) ||
         ( wrapperMode == FBuildOptions::WRAPPER_MODE_NONE ) )
    {
        if ( mainProcess.TryLock() == false )
        {
            if ( options.m_WaitMode == false )
            {
                OUTPUT( "FBuild: Error: Another instance of FASTBuild is already running in '%s'.\\n", options.GetWorkingDir().Get() );
                return FBUILD_ALREADY_RUNNING;
            }

            OUTPUT( "FBuild: Waiting for another FASTBuild to terminate due to -wait option.\\n" );
            while( mainProcess.TryLock() == false )
            {
                Thread::Sleep( 1000 );
                if ( FBuild::GetStopBuild() )
                {
                    return FBUILD_BUILD_FAILED;
                }
            }
        }
    }

    if ( wrapperMode == FBuildOptions::WRAPPER_MODE_MAIN_PROCESS )
    {
        return WrapperMainProcess( options.m_Args, options, finalProcess );
    }

    ASSERT( ( wrapperMode == FBuildOptions::WRAPPER_MODE_NONE ) ||
            ( wrapperMode == FBuildOptions::WRAPPER_MODE_FINAL_PROCESS ) );

		// 打开共享内存区域，并将该区域的指针存储在 **`sharedData`** 变量中。
		// 这个变量在后面的代码中被用于向其他进程发送信息。
    SharedData * sharedData = nullptr;
    if ( wrapperMode == FBuildOptions::WRAPPER_MODE_FINAL_PROCESS )
    {
        while ( !finalProcess.TryLock() )
        {
            OUTPUT( "FBuild: Waiting for another FASTBuild to terminate...\\n" );
            if ( mainProcess.TryLock() )
            {
                // 主进程已终止，退出
                return FBUILD_FAILED_TO_SPAWN_WRAPPER_FINAL;
            }
            Thread::Sleep( 1000 );
        }

        g_SharedMemory.Open( options.GetSharedMemoryName().Get(), sizeof( SharedData ) );

        // 通知“main”进程已经启动
        sharedData = (SharedData *)g_SharedMemory.GetPtr();
        if ( sharedData == nullptr )
        {
            // 主进程在等待期间被杀死
            return FBUILD_FAILED_TO_SPAWN_WRAPPER_FINAL;
        }
        sharedData->Started = true;
    }

    FBuild fBuild( options );

    // 如果有可用的依赖关系图，则加载
    if ( !fBuild.Initialize() )
    {
        if ( sharedData )
        {
            sharedData->ReturnCode = FBUILD_ERROR_LOADING_BFF;
        }
        ctrlCHandler.DeregisterHandler(); // FBuild被销毁之前确保执行
        return FBUILD_ERROR_LOADING_BFF;
    }

		// 下面是一些选项，不多做解释,直接看zui h
		bool result = false;
    if ( options.m_DisplayTargetList )
    {
        fBuild.DisplayTargetList( options.m_ShowHiddenTargets );
        result = true; // DisplayTargetList cannot fail
    }
		else
    {
				// 这里开始编译所选的目标
        result = fBuild.Build( options.m_Targets );
    }

		// 下面则是构建结束后的总结之类的
    // Build Profiling enabled?
    bool problemSavingBuildProfileJSON = false;
    if ( options.m_Profile )
    {
        if ( BuildProfiler::Get().SaveJSON( options, "fbuild_profile.json" ) == false )
        {
            problemSavingBuildProfileJSON = true;
        }
    }

    if ( sharedData )
    {
        sharedData->ReturnCode = ( result == true ) ? FBUILD_OK : FBUILD_BUILD_FAILED;
    }

    // final line of output - status of build
    if ( options.m_ShowTotalTimeTaken )
    {
        const float totalBuildTime = t.GetElapsed();
        const uint32_t minutes = uint32_t( totalBuildTime / 60.0f );
        const float seconds = ( totalBuildTime - (float)( minutes * 60 ) );
        if ( minutes > 0 )
        {
            FLOG_OUTPUT( "Time: %um %05.3fs\n", minutes, (double)seconds );
        }
        else
        {
            FLOG_OUTPUT( "Time: %05.3fs\n", (double)seconds );
        }
    }

    ctrlCHandler.DeregisterHandler(); // Ensure this happens before FBuild is destroyed

    if ( problemSavingBuildProfileJSON )
    {
        return FBUILD_FAILED_TO_WRITE_PROFILE_JSON;
    }    
    return ( result == true ) ? FBUILD_OK : FBUILD_BUILD_FAILED;
}
```

总结一下，该程序执行以下操作：

1. 解析命令行参数
2. 检查是否在“wrapper”模式下运行
3. 检查是否在 Windows 下的 Linux 子系统（Windows Subsystem for Linux, WSL）中运行
4. 将当前进程的优先级设置为 `BELOW_NORMAL_PRIORITY_CLASS`
5. 确保只有一个 `Fastbuild` 实例在运行
6. 如果没有其他 `Fastbuild` 实例正在运行，打开共享内存区域，并将该区域的指针存储在 `sharedData` 变量中。这个变量在后面的代码中被用于向其他进程发送信息。
7. 初始化 `FBuild` 对象
8. 加载依赖关系图
9. 如果启用了 Build Profiling，则保存构建文件的性能分析信息
10. 编译所选的目标
11. 如果出现问题，返回错误代码
12. 显示构建时间

`Main` 函数还包含一些其他的代码，例如处理 `Ctrl+C` 信号和打印错误消息。在最后，`Main` 函数返回一个状态码，以指示构建是否成功。

## `Tools\FBuild\FBuildCore\FBuild.cpp`

`Build 函数解析`

```cpp
// Build
//------------------------------------------------------------------------------
/*virtual*/ bool FBuild::Build( Node * nodeToBuild )
{
    ASSERT( nodeToBuild );
    AtomicStoreRelaxed( &s_StopBuild, false ); // 允许同一个进程中多次运行构建
    AtomicStoreRelaxed( &s_AbortBuild, false ); //允许同一个进程中多次运行构建
    // 创建 JobQueue 对象，并且初始化连接管理系统
    m_JobQueue = FNEW( JobQueue( m_Options.m_NumWorkerThreads ) );

		// 如果是，则创建连接管理系统，如果需要创建，则必须在JobQueue创建后进行
    if ( m_Options.m_AllowDistributed )
    {
				// 通过调用GetSettings()函数从m_DependencyGraph中获取设置节点
				// 
        const SettingsNode * settings = m_DependencyGraph->GetSettings();

        // 使用此节点`settings`的信息获取workers数组，该数组包含要在分布式计算中使用的工作线程列表
        Array< AString > workers( settings->GetWorkerList() );

				// 如果workers数组为空，则通过m_WorkerBrokerage查找可用的工作线程。
        if ( workers.IsEmpty() )
        {
            // check for workers through brokerage or environment
            m_WorkerBrokerage.FindWorkers( workers );
        }

				// 如果仍然没有可用的工作线程，则记录警告并将m_Options.m_AllowDistributed设置为假
        if ( workers.IsEmpty() )
        {
            FLOG_WARN( "No workers available - Distributed compilation disabled" );
            m_Options.m_AllowDistributed = false;
        }
        else
        {
						// 输出可用工作线程的数量以及它们所属的代理的根路径，并创建客户端对象，该对象将被用于与工作线程进行通信。
            OUTPUT( "Distributed Compilation : %u Workers in pool '%s'\n", (uint32_t)workers.GetSize(), m_WorkerBrokerage.GetBrokerageRootPaths().Get() );
						// 创建连接管理系统
            m_Client = FNEW( Client( workers, m_Options.m_DistributionPort, settings->GetWorkerConnectionLimit(), m_Options.m_DistVerbose ) );
        }
    }

		// 设置一些记录时间戳并重置用于跟踪构建进度的一些状态变量
    m_Timer.Start();
    m_LastProgressOutputTime = 0.0f;
    m_LastProgressCalcTime = 0.0f;
    m_SmoothedProgressCurrent = 0.0f;
    m_SmoothedProgressTarget = 0.0f;

		// 调用FLog::StartBuild()函数，该函数负责初始化构建日志记录。
    FLog::StartBuild();
		
    // 如果是主线程直接构建，创建工作线程所需的临时目录
    if ( m_Options.m_NumWorkerThreads == 0 )
    {
        WorkerThread::CreateThreadLocalTmpDir();
    }
		// 启动性能分析器
    if ( BuildProfiler::IsValid() )
    {
        BuildProfiler::Get().StartMetricsGathering();
    }

		// 用来终止构建循环
    bool stopping( false );
    // keep doing build passes until completed/failed
    {
        BuildProfilerScope buildProfileScope( "Build" );

				// 接下来，该函数进入主要循环。
				// 在循环的每个迭代中，该函数首先处理完成的工作，然后执行依赖图扫描以获取更多的工作。
				// 如果不使用工作线程，则调用WorkerThread::Update()函数以更新进度并避免在主线程中挂起。
        for ( ;; )
        {
            // 处理已完成的任务
            m_JobQueue->FinalizeCompletedJobs( *m_DependencyGraph );
            if ( !stopping )
            {
                // 执行一次依赖图扫描，创建更多的工作任务
                m_DependencyGraph->DoBuildPass( nodeToBuild );
            }
						// 如果没有可用的工作线程，则调用WorkerThread::Update()函数以更新进度并避免在主线程中挂起。
            if ( m_Options.m_NumWorkerThreads == 0 )
            {
                // no local threads - do build directly
                WorkerThread::Update();
            }

						// 检查构建过程是否已经完成，即所有目标节点是否已经完成构建或者已经失败
						// Node::UP_TO_DATE 表示节点已经处于最新状态，无需重新构建，因此它应该是构建过程中期望的状态。
						// Node::FAILED 表示节点构建失败，这个状态通常会由节点构建阶段抛出异常或者返回非零的错误码导致。
						// 如果存在任何节点处于 Node::FAILED 状态，构建过程也应该被视为失败，因为构建系统无法完成构建所有目标的任务。
            const bool complete = ( nodeToBuild->GetState() == Node::UP_TO_DATE ) ||
                                  ( nodeToBuild->GetState() == Node::FAILED );

						// 检查是否需要停止构建，可以由外部因素或者上述因素决定
            if ( AtomicLoadRelaxed( &s_StopBuild ) || complete )
            {
                if ( stopping == false )
                {
                    // 释放网络分发系统（如果存在）并发送停止信号给所有工作线程
                    {
                        MutexHolder mh( m_ClientLifetimeMutex );
                        FDELETE m_Client;
                        m_Client = nullptr;
                    }

                    // 等待全部`Woker`节点退出
                    m_JobQueue->SignalStopWorkers();
                    stopping = true;

										// 如果启用了快速取消选项，则还将向系统发出中止构建的信号
                    if ( m_Options.m_FastCancel )
                    {
                    // 通知正在运行的工作线程停止工作并结束构建。该函数采用了原子操作，以保证线程安全。
										// 在这种情况下，构建将立即终止，而不管是否已经完成。这对于在使用 FBuild 的自动化构建系统中，由于某种原因需要取消构建的情况非常有用。
                        AtomicStoreRelaxed( &s_AbortBuild, true );
                    }
                }
            }

						
            if ( !stopping )
            {
								// 如果尚未发出停止信号，就检查是否需要启用 Wrapper Mode，这个模式主要用于在 FBuild.exe 和其他进程之间同步共享资源，
                if ( m_Options.m_WrapperMode == FBuildOptions::WRAPPER_MODE_FINAL_PROCESS )
                {
										// 如果在 FBuild.exe 执行期间 wrapper 进程已经被关闭，就直接中断构建操作。
                    SystemMutex wrapperMutex( m_Options.GetMainProcessMutexName().Get() );
                    if ( wrapperMutex.TryLock() )
                    {
                        // 父进程如果已经推出，构建系统退出
                        AbortBuild();
                    }
                }
            }
            // 如果已经停止了构建操作并且所有的 worker 线程都已经停止，就跳出主循环。
            if ( stopping && m_JobQueue->HaveWorkersStopped() )
            {
                break;
            }

            // 等待一段时间，以便其他线程可以获得资源，避免繁忙的循环浪费 CPU 资源。
            m_JobQueue->MainThreadWait( 500 );

            // 更新构建状态，例如显示进度、输出构建日志等。
            UpdateBuildStatus( nodeToBuild );
        }

        // 检查已经完成的 job 并更新它们的状态。如果有 job 已经完成，它们的输出文件已经生成，就可以更新它们的状态.
				// 如果任务的 Finalize 方法返回 true，则任务节点的状态设置为 Node::UP_TO_DATE，否则设置为 Node::FAILED
				//并检查它们的父节点是否已经准备好构建。如果父节点已经准备好构建，就将它们添加到 job 队列中。
        m_JobQueue->FinalizeCompletedJobs( *m_DependencyGraph );
        FDELETE m_JobQueue;
        m_JobQueue = nullptr;
        FLog::StopBuild();
    }
    if ( BuildProfiler::IsValid() )
    {
        BuildProfiler::Get().StopMetricsGathering();
    }

		// 在构建完成后，无论成功或失败，都可以将依赖图保存到磁盘上，以便在下次构建时重用。
		// 这样可以避免每次构建都需要重新解析 BFF 文件，并且可以记录哪些项目已经构建过，以避免重复构建。
    if ( m_Options.m_SaveDBOnCompletion )
    {
        SaveDependencyGraph( m_DependencyGraphFile.Get() );
    }

    // TODO:C Move this into BuildStats
		// 获得自构建开始以来所用的时间。然后，这个时间被记录到 m_BuildStats 中的 m_TotalBuildTime 字段中
    const float timeTaken = m_Timer.GetElapsed();
    m_BuildStats.m_TotalBuildTime = timeTaken;

		// 这个方法用于记录构建的最终状态和统计信息。
    m_BuildStats.OnBuildStop( nodeToBuild );
    return ( nodeToBuild->GetState() == Node::UP_TO_DATE );
}
```

至此，我们摸清了构建过程的主要工作流程。它包括以下几个步骤：

1. 初始化构建系统，包括创建 JobQueue 对象和连接管理系统等。
2. 执行依赖图扫描，获取工作任务。
3. 处理完成的任务，将它们的状态设置为 `Node::UP_TO_DATE` 或 `Node::FAILED`。
4. 检查是否需要停止构建，如果需要，就释放网络分发系统并发送停止信号给所有工作线程。
5. 等待工作线程退出，释放资源。
6. 更新构建状态，例如显示进度、输出构建日志等。

这段代码的主要目的是实现构建过程的自动化，以提高开发效率和代码质量。FastBuild 构建系统具有高度的可扩展性和灵活性，可以应用于各种不同的项目和场景中。

## `Tools\FBuild\FBuildCore\Graph\Node.h`

先来看下头文件

```cpp
// Node.h - base interface for dependency graph nodes
//------------------------------------------------------------------------------
#pragma once
// Includes
//------------------------------------------------------------------------------
// FBuild
#include "Tools/FBuild/FBuildCore/Graph/Dependencies.h"
// Core
#include "Core/Containers/Array.h"
#include "Core/Reflection/ReflectionMacros.h"
#include "Core/Reflection/Struct.h"
#include "Core/Strings/AString.h"
// Forward Declarations
//------------------------------------------------------------------------------
class BFFToken;
class CompilerNode;
class ConstMemoryStream;
class FileNode;
class Function;
class IMetaData;
class IOStream;
class Job;
class NodeGraph;
// Defines
//------------------------------------------------------------------------------
#define INVALID_NODE_INDEX ( (uint32_t)0xFFFFFFFF )
// Custom Reflection Macros
//------------------------------------------------------------------------------
#define REFLECT_NODE_DECLARE( nodeName )                                \
    REFLECT_STRUCT_DECLARE( nodeName )                                  \
    virtual const ReflectionInfo * GetReflectionInfoV() const override  \
    {                                                                   \
        return nodeName::GetReflectionInfoS();                          \
    }
#define REFLECT_NODE_BEGIN( nodeName, baseNodeName, metaData )          \
    REFLECT_STRUCT_BEGIN( nodeName, baseNodeName, metaData )
#define REFLECT_NODE_BEGIN_ABSTRACT( nodeName, baseNodeName, metaData ) \
    REFLECT_STRUCT_BEGIN_ABSTRACT( nodeName, baseNodeName, metaData )
// FBuild
//------------------------------------------------------------------------------
class Node : public Struct
{
    REFLECT_STRUCT_DECLARE( Node )
    virtual const ReflectionInfo * GetReflectionInfoV() const
    {
        return nullptr; // TODO:B Make pure virtual when everything is using reflection
    }
public:
    enum Type : uint8_t
    {
				PROXY_NODE          = 0, // 代理节点
        COPY_FILE_NODE      = 1, // 复制文件节点
        DIRECTORY_LIST_NODE = 2, // 目录列表节点
        EXEC_NODE           = 3, // 执行节点
        FILE_NODE           = 4, // 文件节点
        LIBRARY_NODE        = 5, // 库节点
        OBJECT_NODE         = 6, // 目标文件节点
        ALIAS_NODE          = 7, // 别名节点
        EXE_NODE            = 8, // 可执行文件节点
        UNITY_NODE          = 9, // Unity 节点
        CS_NODE             = 10, // C# 节点
        TEST_NODE           = 11, // 测试节点
        COMPILER_NODE       = 12, // 编译器节点
        DLL_NODE            = 13, // DLL 节点
        VCXPROJECT_NODE     = 14, // VCX 项目节点
        OBJECT_LIST_NODE    = 15, // 目标文件列表节点
        COPY_DIR_NODE       = 16, // 复制目录节点
        SLN_NODE            = 17, // 解决方案节点
        REMOVE_DIR_NODE     = 18, // 删除目录节点
        XCODEPROJECT_NODE   = 19, // Xcode 项目节点
        SETTINGS_NODE       = 20, // 配置节点
        VSPROJEXTERNAL_NODE = 21, // VS 项目外部节点
        TEXT_FILE_NODE      = 22, // 文本文件节点
        LIST_DEPENDENCIES_NODE = 23, // 列出依赖项节点
        // Make sure you update 's_NodeTypeNames' in the cpp
        NUM_NODE_TYPES      // leave this last
    };
		// 这个枚举类型的作用是表示构建过程中的控制标记。
    enum ControlFlag : uint8_t
    {
        FLAG_NONE                   = 0x00,
        FLAG_ALWAYS_BUILD           = 0x01, // 始终执行DoBuild (for e.g. directory listings)
    };
    enum StatsFlag : uint16_t
    {
        STATS_PROCESSED     = 0x01, // 标记节点已被处理过（用于记录构建过程中的节点处理状态）。
        STATS_BUILT         = 0x02, // 标记节点已被构建（用于记录构建过程中的节点处理状态）。
        STATS_CACHE_HIT     = 0x04, // 标记节点被缓存命中，即需要构建但从缓存中读取到（用于记录构建过程中的节点处理状态）。
        STATS_CACHE_MISS    = 0x08, // 标记节点未被缓存命中，即需要构建但从缓存中未读取到（用于记录构建过程中的节点处理状态）。
        STATS_CACHE_STORE   = 0x10, // 标记节点被存储到缓存中（用于记录构建过程中的节点处理状态）。
        STATS_LIGHT_CACHE   = 0x20, // 标记使用了轻量级缓存（LightCache）
        STATS_BUILT_REMOTE  = 0x40, // 标记节点在远程构建
        STATS_FAILED        = 0x80, // 标记节点构建失败
        STATS_FIRST_BUILD   = 0x100,// 标记节点构建失败
        STATS_REPORT_PROCESSED  = 0x4000, // 标记节点在报告处理期间被处理过
        STATS_STATS_PROCESSED   = 0x8000 // 标记节点在统计收集期间被处理过（用于记录统计收集过程中的节点处理状态）。
    };
    enum BuildResult
    {
        NODE_RESULT_FAILED      = 0,    // 构建过程失败
        NODE_RESULT_NEED_SECOND_BUILD_PASS, // 构建过程需要再次执行
        NODE_RESULT_OK,                 // 构建过程成功完成
        NODE_RESULT_OK_CACHE            // 从缓存中检索成功构建的结果
    };
    enum State : uint8_t
    {
        NOT_PROCESSED,      // 表示任务还没有被处理。这个状态可以被用来表示任务不在当前构建流程中或者等待静态依赖项的处理
        PRE_DEPS_READY,     // 表示任务的前置依赖项已经被处理完毕。在前置依赖项处理完之后，该任务可以被添加到队列中等待后续处理
        STATIC_DEPS_READY,  // 表示任务的静态依赖项都是最新的。在这个状态下，该任务可以开始处理它的动态依赖项
        DYNAMIC_DEPS_DONE,  // 表示任务的动态依赖项已经被更新，但还没有准备好。在这个状态下，任务仍然需要等待动态依赖项完成处理。
        BUILDING,           // 表示任务正在处理中，即被加入了任务队列，并且正在被构建系统进行处理。
        FAILED,             // 表示任务构建失败。当构建系统处理任务失败时，将状态设置为此状态。
        UP_TO_DATE,         // 表示任务已经构建完成并且是最新的。当构建系统确认任务已经是最新状态时，将状态设置为此状态。
    };

		// 下面都是一些声明的函数，暂且略过
		// ------------------------------
protected:
    // Members are ordered to minimize wasted bytes due to padding.
    // Most frequently accessed members are favored for placement in the first cache line.
    AString             m_Name;                     // 节点的全名，由构造函数设置。
    State               m_State = NOT_PROCESSED;    // 节点的状态，初始值为 NOT_PROCESSED，表示没有处理过。
    Type                m_Type;                     // 节点的类型，由构造函数设置。
    mutable uint16_t    m_StatsFlags = 0;           // 用于记录在当前构建中的状态信息，比如该节点是否被处理、是否已构建、是否从缓存中获取等。
																										//可变的 mutable 关键字表示即使在非 const 成员函数中也可以修改该变量。
    mutable uint32_t    m_BuildPassTag = 0;         // 用于防止在单个扫描中多次递归到同一个节点。初始值为 0，表示还没有扫描过该节点。
    uint64_t            m_Stamp = 0;                // 表示此节点的时间戳，用于比较依赖项的时间戳。初始值为 0。
    uint8_t             m_ControlFlags;             // 用于控制构建行为的特殊情况，比如是否始终构建。由构造函数设置。
    bool                m_Hidden = false;           // 标识此节点是否被隐藏（不会在 -showtargets 中显示）。初始值为 false。
    #if defined( DEBUG )
        mutable bool    m_IsSaved = false;          // 帮助捕获错误
    #endif
    // Note: Unused byte here
    uint32_t            m_RecursiveCost = 0;        // 用于任务排序的递归成本。初始值为 0。
    Node *              m_Next = nullptr;           // 在地图中，作为就地链接列表的指针。
    uint32_t            m_NameCRC;                  // m_Name 的哈希值，由构造函数设置。
    uint32_t            m_LastBuildTimeMs = 0;      // 上次完整构建此节点所花费的时间（毫秒）。初始值为 0。
    uint32_t            m_ProcessingTime = 0;       // 用于记录在本次构建中处理该节点所花费的时间。初始值为 0。
    uint32_t            m_CachingTime = 0;          // 用于记录在本次构建中缓存该节点所花费的时间。初始值为 0。
    mutable uint32_t    m_ProgressAccumulator = 0;  // 用于估算构建进度百分比。
    uint32_t            m_Index = INVALID_NODE_INDEX;   // 此节点在所有节点的平面数组中的索引。初始值为 INVALID_NODE_INDEX，表示无效的节点索引。

    Dependencies        m_PreBuildDependencies;  // 前置依赖关系，表示在构建此节点之前需要处理的其他节点。初始为空。
    Dependencies        m_StaticDependencies;    // 静态依赖关系，表示构建此节点时需要的其他节点，它们通常是被包含在该节点的源代码中的其他文件。初始为空。
    Dependencies        m_DynamicDependencies;   // 静态依赖关系，表示构建此节点时需要的其他节点，它们通常是被包含在该节点的源代码中的其他文件。初始为空。

    // Static Data
    static const char * const s_NodeTypeNames[];  // 节点类型的名称数组，用于调试目的。
};
```

可以看出Node 是其他所有节点类的基类，它包含有关依赖项节点的信息，例如节点的状态、类型、时间戳等等。

此外，Node 还定义了一些枚举类型，例如 Type、ControlFlag、StatsFlag 等等，这些枚举类型用于表示节点的类型、构建控制标志、状态信息等等。

Node 还定义了许多成员变量，例如节点的名称、是否隐藏、递归成本等等。

## `Code\Tools\FBuild\FBuildCore\Graph\NodeGraph.h`

接下来看下依赖图是怎么形成的

```cpp
// NodeGraph.h - interface to the dependency graph
// NodeGraphHeader
//------------------------------------------------------------------------------
class NodeGraphHeader
{
public:
    inline explicit NodeGraphHeader()
    {
				// 代码定义了一个名为 m_Identifier 的字符数组，其长度至少为 3 个字符。
				// 这三行代码将 'N'、'G' 和 'D' 分别存储在 m_Identifier 的前三个位置，从而创建了一个以字符串 "NGD" 作为标识符的变量或对象。
				// 通常这种标识符的作用是区分不同的对象或数据类型。
        m_Identifier[ 0 ] = 'N';
        m_Identifier[ 1 ] = 'G';
        m_Identifier[ 2 ] = 'D';
        m_Version = NODE_GRAPH_CURRENT_VERSION;  // // 版本号
        m_Padding = 0;  // 填充
        m_ContentHash = 0;  // 数据的哈希值，不包括这个头部
    }
		// 析构函数
    inline ~NodeGraphHeader() = default;
    enum : uint8_t { NODE_GRAPH_CURRENT_VERSION = 165 };
		// 是否有效
    bool IsValid() const;
		// 版本是否兼容
    bool IsCompatibleVersion() const { return m_Version == NODE_GRAPH_CURRENT_VERSION; }
		// 获取内容的哈希值
    uint64_t    GetContentHash() const          { return m_ContentHash; }
    void        SetContentHash( uint64_t hash ) { m_ContentHash = hash; }
private:
    char        m_Identifier[ 3 ];
    uint8_t     m_Version;
    uint32_t    m_Padding;          // Unused
    uint64_t    m_ContentHash;      // Hash of data excluding this header
};
// NodeGraph
//------------------------------------------------------------------------------
class NodeGraph
{
public:
    explicit NodeGraph();
    ~NodeGraph();
    static NodeGraph * Initialize( const char * bffFile, const char * nodeGraphDBFile, bool forceMigration );
		// 节点的加载结果
    enum class LoadResult
    {
        MISSING_OR_INCOMPATIBLE, // 缺失或不兼容
        LOAD_ERROR,              // 加载错误
        LOAD_ERROR_MOVED,        // 加载错误并移动
        OK_BFF_NEEDS_REPARSING,  // // BFF 需要重新解析
        OK
    };
    // 加载依赖关系
    NodeGraph::LoadResult Load( const char * nodeGraphDBFile );

   // 从内存流中加载依赖关系
    LoadResult Load( ConstMemoryStream & stream, const char * nodeGraphDBFile );
    
	 // 将当前的节点图保存到二进制文件中。MemoryStream 是一个用于在内存中进行读写的类，nodeGraphDBFile 是保存二进制文件的路径。
void Save( MemoryStream & stream, const char * nodeGraphDBFile ) const;
		// 将节点图序列化为文本格式，dependencies 是一个关于节点依赖关系的对象，outBuffer 是用于存储序列化结果的字符串。
    void SerializeToText( const Dependencies & dependencies, AString & outBuffer ) const;
   // 将节点图序列化为 Graphviz DOT 格式的文本，deps 是一个关于节点依赖关系的对象，fullGraph 是一个布尔值，用于控制是否输出整个节点图，outBuffer 是用于存储序列化结果的字符串。
    void SerializeToDotFormat( const Dependencies & deps, const bool fullGraph, AString & outBuffer ) const;
    // access existing nodes
    // 根据节点名称查找节点对象
    Node * FindNode( const AString & nodeName ) const;
    // 根据节点名称查找节点对象，要求名称必须完全匹配
    Node * FindNodeExact( const AString & nodeName ) const;
    // 用于根据索引获取节点对象
    Node * GetNodeByIndex( size_t index ) const;
    // 用于获取节点图中节点的数量
    size_t GetNodeCount() const;
    // 这个方法用于获取与节点图相关的设置信息
    const SettingsNode * GetSettings() const { return m_Settings; }
    // 这个方法用于将新的节点对象注册到节点图中
    void RegisterNode( Node * n );
    // create new nodes
		// 创建一个复制文件的节点，表示将一个文件复制到目标位置
    CopyFileNode * CreateCopyFileNode( const AString & dstFileName );
    // 创建一个复制目录的节点，表示将一个目录及其内容复制到目标位置
    CopyDirNode * CreateCopyDirNode( const AString & nodeName );
    RemoveDirNode * CreateRemoveDirNode( const AString & nodeName );
    // 创建一个执行命令的节点，表示执行指定命令。函数接受命令参数
    ExecNode * CreateExecNode( const AString & dstFileName );
    // 创建一个文件节点，表示将指定文件编译成目标文件。
    // 函数接受文件名参数，并返回指向 FileNode 类型的指针。cleanPath 参数默认为 true，表示应该清除路径中的任何 "." 或 ".."。
    FileNode * CreateFileNode( const AString & fileName, bool cleanPath = true );
    // 创建一个目录列表节点，表示在目录中搜索所有文件并返回其列表。
    DirectoryListNode * CreateDirectoryListNode( const AString & name );
    // 创建一个库文件节点，表示将指定文件编译成库文件
    LibraryNode *   CreateLibraryNode( const AString & libraryName );
    // 创建一个目标文件节点，表示将指定文件编译成目标文件
    ObjectNode *    CreateObjectNode( const AString & objectName );
    // 创建一个别名节点，表示使用另一个节点的名称来引用此节点
    AliasNode *     CreateAliasNode( const AString & aliasName );
    // 创建一个动态链接库（DLL）节点，表示将指定文件编译成 DLL 文件
    DLLNode *       CreateDLLNode( const AString & dllName );
    //用于创建一个可执行文件节点（ExeNode），即生成一个可执行文件
    ExeNode *       CreateExeNode( const AString & exeName );
    // 用于创建一个Unity节点（UnityNode），即将多个源文件合并为一个文件的构建规则。
    // 在Unity构建中，所有源文件都被编译到一个Unity文件中，以减少构建时间和生成的二进制文件大小。
    UnityNode * CreateUnityNode( const AString & unityName );
    // 用于创建一个C#节点（CSNode），即编译C#源代码的构建规则。
    // 在这个节点中，编译器将C#源代码编译成中间语言（IL），然后将中间语言转换为二进制文件。
    CSNode * CreateCSNode( const AString & csAssemblyName );
    TestNode * CreateTestNode( const AString & testOutput );
    // 用于创建一个编译器节点（CompilerNode），即将源代码编译为目标文件的构建规则
    CompilerNode * CreateCompilerNode( const AString & name );
    // 用于创建一个Visual Studio项目节点（VSProjectBaseNode），即用于构建C++项目的构建规则
    VSProjectBaseNode * CreateVCXProjectNode( const AString & name );
    // 用于创建一个外部Visual Studio项目节点（VSProjectBaseNode），即连接到外部Visual Studio项目的构建规则。
    VSProjectBaseNode * CreateVSProjectExternalNode( const AString& name );
    // 用于创建一个解决方案节点（SLNNode），即用于构建Visual Studio解决方案的构建规则
    SLNNode * CreateSLNNode( const AString & name );
    // 该函数创建一个新的ObjectListNode，它是一种节点类型，表示需要编译的目标文件列表
    ObjectListNode * CreateObjectListNode( const AString & listName );
    // 此函数创建一个新的 XCodeProjectNode，这是一种代表 Xcode 项目文件的节点。
    XCodeProjectNode * CreateXCodeProjectNode( const AString & name );
    // 此函数创建一个新的 SettingsNode，这是一种代表一组构建设置的节点
    SettingsNode * CreateSettingsNode( const AString & name );
    // 此函数创建一个新的 ListDependenciesNode，这是一种表示构建目标依赖项列表的节点。
    ListDependenciesNode* CreateListDependenciesNode( const AString& name );
    // 此函数创建一个新的 TextFileNode，这是一种表示文本文件的节点。
    TextFileNode * CreateTextFileNode( const AString & name );

    // 执行编译的函数.划重点
    void DoBuildPass( Node * nodeToBuild );
};
//------------------------------------------------------------------------------
```

接下来看下重点的`DoBuildPass` 函数

### `DoBuildPass`

```cpp
// Build
//------------------------------------------------------------------------------
void NodeGraph::DoBuildPass( Node * nodeToBuild )
{
		// 性能调试
    PROFILE_FUNCTION;
    // 增加全局的build pass tag，它表示当前节点构建的 pass 数。
    s_BuildPassTag++;

		// 如果节点类型是 Node::PROXY_NODE，代表该节点是虚拟节点（proxy node)
		// 即只有在其他节点构建完成后才会构建的节点。
    if ( nodeToBuild->GetType() == Node::PROXY_NODE )
    {
				// 获取代理节点的静态依赖项总数
        const size_t total = nodeToBuild->GetStaticDependencies().GetSize();
        // 已构建但失败的依赖项数
        size_t failedCount = 0;
        size_t upToDateCount = 0;
        // 获取代理节点的所有静态依赖项
        const Dependency * const end = nodeToBuild->GetStaticDependencies().End();
				// 遍历依赖项
        for ( const Dependency * it = nodeToBuild->GetStaticDependencies().Begin(); it != end; ++it )
        {
            Node * n = it->GetNode();
            // 如果依赖项的状态不是构建中（BUILDING）状态
            if ( n->GetState() < Node::BUILDING )
            {
								// 递归地构建依赖项
                BuildRecurse( n, 0 );
            }
            // 检查递归后的结果（可能完成也可能不完成）
            if ( n->GetState() == Node::UP_TO_DATE )
            {
                upToDateCount++;
            }
            else if ( n->GetState() == Node::FAILED )
            {
                failedCount++;
            }
        }
        // 只有当所有依赖项都已经完成（无论成功或失败）
        if ( ( upToDateCount + failedCount ) == total )
        {
            // 当所有子节点都处于UP_TO_DATE状态时，代理节点也应该被标记为UP_TO_DATE。当有任何一个子节点处于FAILED状态时，代理节点也应该被标记为FAILED。
            nodeToBuild->SetState( failedCount ? Node::FAILED : Node::UP_TO_DATE );
        }
    }
    else  // 如果不是代理节点
    {
        // 如果当前节点的状态小于Node::BUILDING，说明该节点还未开始构建，需要递归地构建该节点及其依赖项。
        if ( nodeToBuild->GetState() < Node::BUILDING )
        {
				// 递归构建Node及其依赖项的函数调用。这个函数会将当前节点及其依赖项添加到作业队列中，通过调用构建工作线程来构建它们。
				// 此函数会先递归构建当前节点的依赖项，直到依赖项被构建完成。
				// 然后，它将检查当前节点是否需要重新构建，并将当前节点添加到作业队列中等待执行。在构建完成后，BuildRecurse()函数返回，控制权回到DoBuildPass()函数。
            BuildRecurse( nodeToBuild, 0 );
        }
    }
    // 检查是否存在运行时可发现的循环依赖关系
		// 在构建完成后检查是否存在循环依赖，如果存在循环依赖，则中止整个构建过程，防止出现无限循环的构建过程。
    if ( CheckForCyclicDependencies( nodeToBuild ) )
    {
				// 如果存在则终止构建
        FBuild::AbortBuild();
    }
    // 在本次构建过程中发现的所有Job都可以使用了
    JobQueue::Get().FlushJobBatch();
}
```

**`DoBuildPass`**函数是NodeGraph类的一个成员函数，它的作用是执行一次构建过程，构建给定的节点及其所有依赖项。以下是**`DoBuildPass`**函数的工作流程：

1. 将s_BuildPassTag增加1，以便在构建过程中为所有Node设置s_BuildPassTag，以便在下一次构建过程中检测哪些Node需要重新构建。
2. 如果要构建的节点是一个代理节点（Proxy Node），则需要构建它的所有静态依赖项。循环遍历每个依赖项，并递归地调用**`BuildRecurse`**函数构建依赖项及其所有依赖项。在遍历完成所有依赖项后，检查它们的状态并根据状态设置节点的状态。
3. 如果要构建的节点不是代理节点，则只需要递归调用**`BuildRecurse`**函数构建该节点及其所有依赖项。
4. 检查是否存在循环依赖项，如果存在，则中止构建过程。
5. 将在本次构建过程中发现的所有作业（Job）批量提交给作业队列。

再来看下是如何将构建任务提交到`JobQueue`的

### **`BuildRecurse`**

```cpp
// BuildRecurse
//------------------------------------------------------------------------------
void NodeGraph::BuildRecurse( Node * nodeToBuild, uint32_t cost )
{
		// 检查是否已经做好编译准备
    ASSERT( nodeToBuild );
    ASSERT( nodeToBuild->GetState() != Node::BUILDING );
    // 增加节点上一次构建的时间到递归成本中
    cost += nodeToBuild->GetLastBuildTime();
    // 检查节点的预构建依赖项
    if ( nodeToBuild->GetState() == Node::NOT_PROCESSED )
    {
        // 检查节点的前置依赖是否已经准备好。
        const bool allDependenciesUpToDate = CheckDependencies( nodeToBuild, nodeToBuild->GetPreBuildDependencies(), cost );
        if ( allDependenciesUpToDate == false )
        {
						// 表示当前节点还没有准备好构建，或者前置依赖已经过期或失败，所以函数将直接返回。
            return;
        }
				// 表示前置依赖已经准备好
        nodeToBuild->SetState( Node::PRE_DEPS_READY );
    }
		// 再一次检查节点是否做好准备
    ASSERT( ( nodeToBuild->GetState() == Node::PRE_DEPS_READY ) ||
            ( nodeToBuild->GetState() == Node::STATIC_DEPS_READY ) ||
            ( nodeToBuild->GetState() == Node::DYNAMIC_DEPS_DONE ) );

    // 检查静态依赖关系（即在构建当前节点之前必须已经构建的节点），并检查它们是否都已经构建完毕。
		// 检查当前节点的状态是否为 Node::PRE_DEPS_READY，这表示所有前置依赖关系（pre-build dependencies）都已经准备好，可以开始检查静态依赖关系。
		// 如果节点状态不是 Node::PRE_DEPS_READY，则说明节点已经被标记为“正在构建”或者“已经在构建队列中”，就不需要再次检查静态依赖关系了。
    if ( nodeToBuild->GetState() == Node::PRE_DEPS_READY )
    {
        // 检查所有静态依赖关系是否都已经构建完毕
        const bool allDependenciesUpToDate = CheckDependencies( nodeToBuild, nodeToBuild->GetStaticDependencies(), cost );

				// 如果存在任何一个静态依赖关系没有构建完毕，则返回，表示当前节点还没有准备好构建。
        if ( allDependenciesUpToDate == false )
        {
            return; // not ready or failed
        }
				
				// 将节点状态设置为 Node::STATIC_DEPS_READY，表示所有静态依赖关系都已经构建完毕。
        nodeToBuild->SetState( Node::STATIC_DEPS_READY );
    }

		// 
    ASSERT( ( nodeToBuild->GetState() == Node::STATIC_DEPS_READY ) ||
            ( nodeToBuild->GetState() == Node::DYNAMIC_DEPS_DONE ) );

		// 检查节点是否已经完成动态依赖项，如果没有完成，则需要重新生成动态依赖项。
		// 这里的作用是尽可能减少不必要的重新生成动态依赖的次数，以提高构建效率。
		// 只有在节点的状态或静态依赖关系发生更改时才需要重新生成动态依赖。如果节点需要重新构建，动态依赖关系需要重新生成，因为一些动态依赖关系可能会随运行变化而变化。
    if ( nodeToBuild->GetState() != Node::DYNAMIC_DEPS_DONE )
    {
        // 如果静态依赖项要求被重新构建，则也需要重新生成动态依赖项
				// 确保节点的所有依赖项都是最新的，因为静态依赖项的更改可能导致动态依赖项也需要重新生成
        const bool forceClean = FBuild::Get().GetOptions().m_ForceCleanBuild;
        if ( forceClean ||
             nodeToBuild->DetermineNeedToBuildStatic() )
        {
            // 清除动态依赖项
            nodeToBuild->m_DynamicDependencies.Clear();
						// 明确标记节点，以便在构建此节点之前取消构建时重建
            if ( nodeToBuild->m_Stamp == 0 )
            {
								// 注意，这是我们第一次构建（因为节点无法检查标记，因为我们在下面清除它）
                nodeToBuild->SetStatFlag( Node::STATS_FIRST_BUILD );
            }
						// 将节点的时间戳设置为0
						// 如果节点的时间戳比其所有依赖节点的时间戳都要旧，那么节点就需要重新构建。在清空动态依赖关系后，因为时间戳被重置为 0，所以这个节点必须被重新构建。
            nodeToBuild->m_Stamp = 0;
            // 重新生成动态依赖项
            if ( nodeToBuild->DoDynamicDependencies( *this, forceClean ) == false )
            {
                nodeToBuild->SetState( Node::FAILED );
                return;
            }
            // 继续检查动态依赖项和构建
        }
        // 动态依赖项已经检查完毕了
        nodeToBuild->SetState( Node::DYNAMIC_DEPS_DONE );
    }

    ASSERT( nodeToBuild->GetState() == Node::DYNAMIC_DEPS_DONE );
    // 检查节点的动态依赖项是否已经最新，如果存在动态依赖项没有准备好（即它们不是最新的），则直接返回，这意味着该节点不能被构建，必须等待动态依赖项准备好。
    {
        // all static deps done?
        const bool allDependenciesUpToDate = CheckDependencies( nodeToBuild, nodeToBuild->GetDynamicDependencies(), cost );
        if ( allDependenciesUpToDate == false )
        {
            return; // not ready or failed
        }
    }

    // 当前节点的所有依赖都是最新的，可以构建该节点
		// 节点的状态设置为已处理（STATS_PROCESSED），表示该节点已被处理过。
    nodeToBuild->SetStatFlag( Node::STATS_PROCESSED );
		// 如果当前节点的时间戳为0或者需要动态生成依赖，则需要构建该节点。
    if ( ( nodeToBuild->GetStamp() == 0 ) ||
         nodeToBuild->DetermineNeedToBuildDynamic() )
    {
				// 设置该节点的递归成本
        nodeToBuild->m_RecursiveCost = cost;
				// 将节点添加到任务队列中
        JobQueue::Get().AddJobToBatch( nodeToBuild );
    }
		// 如果节点不需要构建，则将节点的状态设置为UP_TO_DATE，
		// 并在日志中输出Up-To-Date信息（如果开启了Verbose模式）表示该节点已经是最新的，不需要再构建了。
    else
    {
        if ( FLog::ShowVerbose() )
        {
            FLOG_BUILD_REASON( "Up-To-Date '%s'\n", nodeToBuild->GetName().Get() );
        }
        nodeToBuild->SetState( Node::UP_TO_DATE );
    }
}
```

总结一下，**`BuildRecurse`** 函数是一个递归函数，用于递归构建节点的依赖项。他的工作流程和分支分别是：

1. 检查节点的有效性和状态，如果已经处于构建状态则断言失败，如果未被处理过，则检查其预构建依赖项。
2. 如果节点的预构建依赖项未准备好，则递归处理其预构建依赖项。
3. 检查节点的状态，如果节点的状态为“预构建依赖项已准备就绪”，则检查其静态依赖项。
4. 如果节点的静态依赖项未准备好，则递归处理其静态依赖项。
5. 如果节点的状态不是“动态依赖项已完成”，则根据需要重新生成其动态依赖项。
6. 检查节点的动态依赖项是否准备好，如果未准备好，则返回。
7. 检查节点是否需要重新构建，如果需要，则将其加入作业队列中。
8. 如果节点不需要重新构建，则将其状态设置为“已更新”。

在执行递归构建时，该函数会沿着依赖树向下递归，直到所有依赖项都被处理。在处理每个节点时，函数会检查其依赖项是否已经准备好，并在需要时重新生成其动态依赖项。

如果所有依赖项都准备就绪，则检查节点是否需要重新构建。如果需要重新构建，则将其添加到作业队列中；否则将其标记为“已更新”。

## `Tools\FBuild\FBuildCore\WorkerPool\JobQueue.h`

**`JobQueue` 主要功能是用于管理作业的执行。**

**作业可以是本地执行的，也可以是分布式执行的。**

**下面列举几个跟任务队列有关的函数:**

- **`AddJobToBatch`**：将新的作业添加到暂存队列中。
- **`FlushJobBatch`**：对暂存队列中的作业进行排序，并将其推送到可用队列中。
- **`HasJobsToFlush`**：判断是否有暂存的作业需要刷新。
- **`FinalizeCompletedJobs`**：将已完成的作业提交到节点图中进行更新。
- **`MainThreadWait`**：主线程等待直到有可用的作业。
- **`WakeMainThread`**：唤醒主线程。
- **`SignalStopWorkers`**：通知工作线程停止运行。
- **`HaveWorkersStopped`**：检查工作线程是否已停止。
- **`GetNumDistributableJobsAvailable`**：获取当前可分配的作业数量。
- **`GetJobStats`**：获取有关作业状态的统计信息。
- **`HasPendingCompletedJobs`**：判断是否有已完成的作业等待处理。
- `DoBuild`: 重点函数，后面会讲到

此外，该类还有一些私有方法，主要用于工作线程和客户端（消费者）访问和操作作业队列。其中，**`WorkerThread`**是一个辅助类，用于管理工作线程的创建和销毁。类中使用了一些同步对象，例如互斥锁和信号量，用于保证多线程之间的同步和互斥。

## `Tools\FBuild\FBuildCore\WorkerPool\JobQueue.cpp`

### `Dobuild`

> 这里是本地执行构建的核心函数
> 

```cpp
// DoBuild
//------------------------------------------------------------------------------
/*static*/ Node::BuildResult JobQueue::DoBuild( Job * job )
{
		// 创建一个计时器，用于测量任务的执行时间。
    const Timer timer;
		// 获取任务目标
    Node * node = job->GetNode();

		// 检查当前 Node 的类型是否是构建监控记录（monitor log）中需要记录的类型。
		// 如果是，则将 nodeRelevantToMonitorLog 设为 true，并记录该 Node 的开始构建操作到监控记录中。
    bool nodeRelevantToMonitorLog = false;
    const AString & nodeName = job->GetNode()->GetName();
    if ( ( node->GetType() == Node::OBJECT_NODE ) ||
         ( node->GetType() == Node::EXE_NODE ) ||
         ( node->GetType() == Node::LIBRARY_NODE ) ||
         ( node->GetType() == Node::DLL_NODE ) ||
         ( node->GetType() == Node::CS_NODE ) ||
         ( node->GetType() == Node::EXEC_NODE ) ||
         ( node->GetType() == Node::TEST_NODE ) )
    {
        nodeRelevantToMonitorLog = true;
        FLOG_MONITOR( "START_JOB local \"%s\" \n", nodeName.Get() );
    }
		
		// 如果节点表示的是一个输出文件（即非输入文件），则确保输出路径存在。如果输出路径不存在，则返回“失败”。
    const bool isOutputFile = node->IsAFile() && ( node->GetType() != Node::FILE_NODE );
    if ( isOutputFile )
    {
        if ( Node::EnsurePathExistsForFile( node->GetName() ) == false )
        {
            // error already output by EnsurePathExistsForFile
            return Node::NODE_RESULT_FAILED;
        }
    }

		// 检查构建选项中的 m_FastCancel 是否启用，以及是否已经停止了构建。
    Node::BuildResult result;
    if ( FBuild::Get().GetOptions().m_FastCancel && FBuild::GetStopBuild() )
    {
		// 如果是，则将 result 设为 Node::NODE_RESULT_FAILED，表示构建失败。
		// m_FastCancel 是一个可选的构建选项，它允许构建被取消的更快。如果 m_FastCancel 启用，则构建会尽快停止，而不会等待正在运行的工作完成。
        result = Node::NODE_RESULT_FAILED;
    }
    else
    {
				// 如果启用了性能分析，则使用 PROFILE_SECTION 宏记录 profilingTag，以便进行后续分析。
				// PROFILE_SECTION 宏实际上是一个计时器，用于测量代码段的执行时间。
        #ifdef PROFILING_ENABLED
            const char * profilingTag = node->GetTypeName();
						// 如果节点是 OBJECT_NODE 类型，则进一步检查它是否正在创建预编译头文件（IsCreatingPCH()）或者是否正在使用预编译头文件（IsUsingPCH()），并相应地设置 profilingTag。
            if ( node->GetType() == Node::OBJECT_NODE )
            {
                const ObjectNode * on = (ObjectNode *)node;
                profilingTag = on->IsCreatingPCH() ? "PCH" : on->IsUsingPCH() ? "Obj (+PCH)" : profilingTag;
            }
            PROFILE_SECTION( profilingTag );
        #endif

				// BuildProfilerScope 是另一个性能分析对象，它记录了某个节点的构建时间。
        BuildProfilerScope profileScope( *job, WorkerThread::GetThreadIndex(), node->GetTypeName() );
				// DoBuild() 方法是 Node 类的虚函数，它实现了节点的实际构建过程。
				// DoBuild() 方法的返回值 result 是一个枚举类型 Node::BuildResult，它表示构建的结果。
        result = node->DoBuild( job );
    }

		// 获取构建过程中花费的时间
    const uint32_t timeTakenMS = uint32_t( timer.GetElapsedMS() );
		// 这里已经构建完成了，如果我们想发送构建信息比如时间和结果及其节点类型到其他出口，在这里添加代码
    if ( result == Node::NODE_RESULT_OK )
    {
				// 将时间记录到节点的最后构建时间
        node->SetLastBuildTime( timeTakenMS );
				// 设置节点的状态为已构建
        node->SetStatFlag( Node::STATS_BUILT );
				// 输出一条信息记录构建所需的时间和构建的节点的名称
        FLOG_VERBOSE( "-Build: %u ms\t%s", timeTakenMS, node->GetName().Get() );
    }

		// 如果构建失败，则设置状态为失败
    if ( result == Node::NODE_RESULT_FAILED )
    {
        node->SetStatFlag( Node::STATS_FAILED );
    }
		// 如果需要进行第二次构建，则不执行任何操作。
    else if ( result == Node::NODE_RESULT_NEED_SECOND_BUILD_PASS )
    {
        // nothing to check
    }
    else 
    {
				// 构建成功或从缓存中检索到了
        ASSERT( ( result == Node::NODE_RESULT_OK ) || ( result == Node::NODE_RESULT_OK_CACHE ) );
        // 如果节点表示的是一个文件（而不是一个目录），则确保文件存在于磁盘上。
        if ( node->IsAFile() )
        {
            // 如果节点不是一个文件节点类型，则会忽略该节点，因为它表示的是一个目录或虚拟节点
            if ( node->GetType() != Node::FILE_NODE )
            {
                // 如果文件不存在，将会发出错误日志并将 result 设置为 NODE_RESULT_FAILED，因为文件不存在表示构建过程出现了错误。
                if ( !FileIO::FileExists( node->GetName().Get() ) )
                {
                    FLOG_ERROR( "File missing despite success for '%s'", node->GetName().Get() );
                    result = Node::NODE_RESULT_FAILED;
                }
            }
        }
    }
		// 这个检查的考虑是确保构建过程中生成的文件确实存在，以便在后续构建中能够正确使用。
		// 如果文件在构建过程中被意外地删除或移动，就会导致构建失败。
		// 此外，这个检查还可以帮助发现构建逻辑中的问题，例如，在某些情况下，构建过程可能会意外地生成了错误的文件名或路径。

    // 将节点的处理时间加入节点对象中，以便统计节点的平均处理时间等信息。
    node->AddProcessingTime( timeTakenMS );
		// 判断节点是否与监视器日志相关，并且监视器日志是否启用。
    if ( nodeRelevantToMonitorLog && FLog::IsMonitorEnabled() )
    {
				// 将处理结果、节点名称和作业消息记录到监视器日志中。
        const char * resultString = nullptr;
        switch ( result )
        {
            case Node::NODE_RESULT_OK:                      resultString = "SUCCESS_COMPLETE";      break;
            case Node::NODE_RESULT_NEED_SECOND_BUILD_PASS:  resultString = "SUCCESS_PREPROCESSED";  break;
            case Node::NODE_RESULT_OK_CACHE:                resultString = "SUCCESS_CACHED";        break;
            case Node::NODE_RESULT_FAILED:                  resultString = "FAILED";                break;
        }
        AStackString<> msgBuffer;
        job->GetMessagesForMonitorLog( msgBuffer );
        FLOG_MONITOR( "FINISH_JOB %s local \"%s\" \"%s\"\n",
                      resultString,
                      nodeName.Get(),
                      msgBuffer.Get() );
    }
    return result;
}
```

`DoBuild`函数是 FBuild 构建系统中的一个核心函数，它用于实际构建一个节点表示的文件或目标。其主要的工作流程包括以下几个步骤：

1. 检查节点的依赖关系，如果有必要则构建依赖节点。

2. 如果节点已经构建过，并且缓存没有过期，则使用缓存结果，直接返回。

3. 如果节点需要进行二次构建，则先进行一次预处理构建。

4. 如果节点不需要构建，直接返回成功。
否则，调用节点的构建函数实际进行构建。

根据这些步骤，`DoBuild`函数的不同分支可以归纳如下：

1. 节点已经构建过，并且缓存没有过期：直接返回缓存结果（NODE_RESULT_OK_CACHE）。

2. 节点需要进行二次构建：进行一次预处理构建，然后再进行正式构建，这时需要检查构建结果。

3. 节点不需要构建：直接返回成功（NODE_RESULT_OK）。

4. 节点需要构建：调用节点的构建函数进行构建，并检查构建结果。构建成功返回成功（NODE_RESULT_OK），构建失败返回失败（NODE_RESULT_FAILED）。

最后，该函数根据资源构建的结果向监视器日志记录相关的消息，并返回节点的状态。

## `Tools\FBuild\FBuildCore\WorkerPool\JobQueueRemote.cpp`

> 上面介绍完本地构建，接下来看下比较复杂的远程构建
> 

### `DoBuild`

```cpp
// DoBuild
//------------------------------------------------------------------------------
/*static*/ Node::BuildResult JobQueueRemote::DoBuild( Job * job, bool racingRemoteJob )
{
		// 创建一个 BuildProfilerScope 对象，用于记录构建时间和执行线程等信息
    BuildProfilerScope profileScope( *job, WorkerThread::GetThreadIndex(), job->GetNode()->GetTypeName() );
		// 创建一个 Timer 对象，用于记录构建时间
    const Timer timer; // track how long the item takes
    // 根据任务类型，获取节点对象。
    ObjectNode * node = job->GetNode()->CastTo< ObjectNode >();

		// 如果 Job 在本地执行，则打印构建开始日志
    if ( job->IsLocal() )
    {
        FLOG_MONITOR( "START_JOB local \"%s\" \n", job->GetNode()->GetName().Get() );
    }

		
    // 如果是远程任务，需要将输出结果写入到临时文件中。
    if ( job->IsLocal() == false )
    {
        // 获取 Job 在远程机器上的文件名，并在本地创建对应的临时文件
        const char * fileName = ( job->GetRemoteName().FindLast( NATIVE_SLASH ) + 1 );
        AStackString<> tmpFileName;
        WorkerThread::CreateTempFilePath( fileName, tmpFileName );
				// 将 ObjectNode 的文件名替换为临时文件的文件名
        node->ReplaceDummyName( tmpFileName );
        //DEBUGSPAM( "REMOTE: %s (%s)\n", fileName, job->GetRemoteName().Get() );
    }

		// 确保节点是文件类型而不是目录类型
    ASSERT( node->IsAFile() );
    // 确保输出文件所在路径存在
    if ( Node::EnsurePathExistsForFile( node->GetName() ) == false )
    {
        // 如果无法创建输出文件所在路径，则返回构建失败
        return Node::NODE_RESULT_FAILED;
    }
    // 如果该 ObjectNode 使用了 PDB 文件，并且 Job 在远程机器上执行，则删除旧的 PDB 文件，以确保没有旧数据残留
   // PDB是微软平台上的一种调试信息文件，它包含了与程序代码相关的调试信息，例如源代码行号、变量名称、函数名称以及类型信息等。这些信息可以帮助开发人员在调试和分析代码时更容易地理解程序行为和问题原因。PDB文件通常与可执行文件一起生成，并且在程序崩溃或出现错误时，可以被调试器自动加载并使用。
    if ( node->IsUsingPDB() && ( job->IsLocal() == false ) )
    {
        AStackString<> pdbName;
        node->GetPDBName( pdbName );
        FileIO::FileDelete( pdbName.Get() );
    }

		// 执行构建任务，获取构建结果
    Node::BuildResult result;
    {
        PROFILE_SECTION( racingRemoteJob ? "RACE" : "LOCAL" );
				// 这里调用是远程构建函数，本地构建函数是 DoBuild
        result = ((Node *)node )->DoBuild2( job, racingRemoteJob );
    }

    // 如果任务已经被取消，忽略任务执行结果。
		// 在分布式构建中，可能会发生本地执行任务失败但是远程任务已经完成的情况，此时需要忽略本地执行任务的失败结果。具体情况如下：

		// 当一个任务被分发到远程节点上并且远程节点已经完成了该任务，但是该任务的本地执行节点在此期间由于某种原因失败了。此时，调度器将该任务标记为 "DIST_RACE_WON_REMOTELY_CANCEL_LOCAL"，这个标记表示远程任务已经完成且本地任务已被取消。

		// 在这种情况下，如果任务的结果为 Node::NODE_RESULT_FAILED，那么该结果将被忽略并直接返回 Node::NODE_RESULT_FAILED，否则将会继续处理该任务的结果。这是因为在这种情况下，本地任务的失败已经被远程任务成功所替代，因此忽略本地任务的失败结果。
    if ( job->GetDistributionState() == Job::DIST_RACE_WON_REMOTELY_CANCEL_LOCAL )
    {
				// 取消了还失败，直接返回构建失败
        if ( result == Node::NODE_RESULT_FAILED )
        {
            return Node::NODE_RESULT_FAILED;
        }
    }

		// 记录从开头到现在所花费的时间
    const uint32_t timeTakenMS = uint32_t( timer.GetElapsedMS() );
    if ( result == Node::NODE_RESULT_FAILED )
    {
				// 如果构建失败，它首先检查是否需要记录时间。因为在本地构建失败时，我们不想记录构建时间。
				// 相反，我们希望保留上一次成功构建的时间，以便正确地排序作业。但是，如果在远程构建，则需要记录时间，因此这里对是否在本地进行了检查。
        if ( job->IsLocal() == false )
        {
            node->SetLastBuildTime( timeTakenMS );
        }
				// 代码设置节点的状态为失败
        node->SetStatFlag( Node::STATS_FAILED );
    }
    else
    {
        // build completed ok
        ASSERT( result == Node::NODE_RESULT_OK );
        // 记录新的构建时间
        node->SetLastBuildTime( timeTakenMS );
        node->SetStatFlag( Node::STATS_BUILT );
        #ifdef DEBUG
            if ( job->IsLocal() )
            {
								// 在本地构建远程作业时，检查构建后生成的输出文件的时间戳是否与该节点的时间戳一致。
								// 这是为了确保在本地构建远程作业时，该节点生成的文件与在远程服务器上生成的文件相同。
								// 如果该时间戳不匹配，则可能表明在本地构建过程中出现了问题，需要进行调查。通过此断言，可以在构建期间及早发现此类问题，以便及时修复。
                ASSERT( node->m_Stamp == FileIO::GetFileLastWriteTime(node->GetName()) );
            }
        #endif
        // TODO:A Also read into job if cache is being used
        if ( job->IsLocal() == false )
        {
            // 读取结果到内存中以便发送给客户端
            if ( ReadResults( job ) == false )
            {
                result = Node::NODE_RESULT_FAILED;
            }
        }
    }

    // 清理在远程构建的临时文件和调试信息
    if ( job->IsLocal() == false )
    {
        // Cleanup obj file
        FileIO::FileDelete( node->GetName().Get() );
        // Cleanup PDB file
        if ( node->IsUsingPDB() )
        {
            AStackString<> pdbName;
            node->GetPDBName( pdbName );
            FileIO::FileDelete( pdbName.Get() );
        }
    }

    // 记录该节点花费的总时间
    node->AddProcessingTime( timeTakenMS );
		// 监视日志是用于本地记录的，所以只有在本地构建的情况下才需要记录监视日志。
		// 如果是在远程机器上构建，则记录监视日志没有实际意义。
    if ( job->IsLocal() && FLog::IsMonitorEnabled() )
    {
        AStackString<> msgBuffer;
        job->GetMessagesForMonitorLog( msgBuffer );
        FLOG_MONITOR( "FINISH_JOB %s local \"%s\" \"%s\"\n",
                      ( result == Node::NODE_RESULT_FAILED ) ? "ERROR" : "SUCCESS",
                      job->GetNode()->GetName().Get(),
                      msgBuffer.Get());
    }
    return result;
}
```

# 进度获取

看完内部结构后，如果想获取每个`job` 的开始，构建时间，结束还是有难度的

而且远程构建中是无法获取准确的数据，不过我们还是有办法获取到远程`job` 的节点名称和构建时间

好在FASTBuild 有自带的monitor 类，这里只需要修改几处就能获取本地构建和远程构建的时间和额外信息

### `Tools\FBuild\FBuildCore\WorkerPool\JobQueue.cpp`

> 获取本地job的开始
> 

```cpp
// DoBuild
//------------------------------------------------------------------------------
/*static*/ Node::BuildResult JobQueue::DoBuild( Job * job )
{
// ...
// 下面这里开始记录本地job的开始
{
        nodeRelevantToMonitorLog = true;
        FLOG_MONITOR( "START_JOB local \"%s\" \n", nodeName.Get() );
    }
}
```

> 获取本地job的结束
> 

```cpp
// DoBuild
//------------------------------------------------------------------------------
/*static*/ Node::BuildResult JobQueue::DoBuild( Job * job )
{
// ...
if ( nodeRelevantToMonitorLog && FLog::IsMonitorEnabled() )
    {
// 下面这里就是result_ok 的结束
FLOG_MONITOR( "FINISH_JOB %s local \"%s\" \"%s\" BuildTimeMs: %ums ProcessingTime: %ums \n",
                      resultString,
                      nodeName.Get(),
                      msgBuffer.Get(),
                      node->GetLastBuildTime(),
                      node->GetProcessingTime() );
}
}
```

### `Tools\FBuild\FBuildCore\Protocol\Client.cpp`

> 获取远程job的开始
> 

```cpp
// Process( MsgRequestJob )
//------------------------------------------------------------------------------
void Client::Process( const ConnectionInfo * connection, const Protocol::MsgRequestJob * )
{
// ...
// 下面这里就是开始记录job的开始
FLOG_MONITOR( "START_JOB %s \"%s\" \n", ss->m_RemoteName.Get(), job->GetNode()->GetName().Get() );
}
```

> 获取远程 job 的结束
> 

```cpp
// ProcessJobResultCommon
//------------------------------------------------------------------------------
void Client::ProcessJobResultCommon( const ConnectionInfo * connection, bool isCompressed, const void * payload, size_t payloadSize )
{
// ...
if ( FLog::IsMonitorEnabled() )
    {
        AStackString<> msgBuffer;
        Job::GetMessagesForMonitorLog( messages, msgBuffer );
				// 下面这里就是result_ok 的结束
        FLOG_MONITOR( "FINISH_JOB %s %s \"%s\" \"%s\" BuildTimeMs: %ums ProcessingTime: %ums\n",
                      result ? "SUCCESS" : "ERROR",
                      ss->m_RemoteName.Get(),
                      node->GetName().Get(),
                      msgBuffer.Get(),
                      node->GetLastBuildTime(),
                      node->GetProcessingTime() );
    }
}
```

# 总结

---

- 两个文件 `Job.h` 和 `Job.cpp` 定义和实现了一个 C++ 类 (`Job`)，
它代表了工具执行的单个步骤，也称为“作业”。
每个“作业”对应于构建图中的一个节点，可能表示编译源文件、链接目标文件、复制文件等任务，
以及其依赖项和输出文件。
`Job` 类的构造函数接受一个 `Node` 参数，表示要执行作业的节点。
此类还定义了一些函数，如 `CancelDueToRemoteRaceWin`，用于在分布式构建中取消本地作业以解决远程竞争，
以及 `GetMessagesForLog`，用于在输出日志中显示与作业相关的消息。
- `Graph.h` 和 `Graph.cpp`，它们定义和实现了一个代表“构建图”的 C++ 类（`Graph`），用于表示整个构建过程。它由一组 `Node` 对象组成，每个 `Node` 代表构建图中的一个步骤（如编译一个源文件或链接一个目标文件），并且可能依赖于其他 `Node` 对象。`Graph` 类提供了一组接口，用于添加、删除和查询 `Node` 对象。
- `Node.h` 和 `Node.cpp`，它们定义和实现了一个代表“节点”的 C++ 类（`Node`），用于表示构建图中的一个步骤。每个 `Node` 对象都有一个名称，可能有一些依赖项（表示源文件或其他节点），也可能有一些输出项（表示编译后的目标文件或其他节点）。`Node` 类的方法用于添加、删除和查询依赖项和输出项，以及计算“节点”是否需要重新构建。
- `FBuild.cpp`，它是整个构建工具的入口点。它实例化了一个 `Graph` 对象，添加所有需要构建的 `Node` 对象，然后执行整个构建过程。
- `FLog.h` 和 `FLog.cpp`，它们定义和实现了一个代表“日志”的 C++ 类（`FLog`），用于输出构建过程的信息和错误消息。它的静态方法用于记录和输出信息，例如 `Error`, `Warning`, `Debug`, `DebugDirect`, `Info`, `Progress` 等等。