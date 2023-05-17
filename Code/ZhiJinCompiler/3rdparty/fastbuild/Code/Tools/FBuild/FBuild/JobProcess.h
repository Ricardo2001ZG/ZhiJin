//------------------------------------------------------------------------------
#pragma once

#include "Core/Reflection/Struct.h"
#include "Core/Strings/AString.h"
#include "Core/Process/Semaphore.h"
#include "Tools/FBuild/FBuild/channel.h"
//#include "Tools/FBuild/FBuildCore/Graph/Node.h"

class JobProcess
{
public:
        // 构建任务状态
        enum class job_status : uint8_t
        {
                process = 0,
                success = 1,
                failed = 2,
                cache = 3,
        };


        enum class job_type : uint8_t
        {
                job=0,  // 构建任务
                other, // 纯文字，一般用于最后的总结
        };

        // 构建位置
        enum class job_location: uint8_t{
                local=0,
                remote,
        };

        JobProcess();
        JobProcess(const AString name, job_status _status, job_type _type,uint32_t _index);
        ~JobProcess();

        inline const char *GetName() const { return m_Name.Get(); }
        inline void SetName(const AString name) { m_Name = name; };
        inline void SetStatus(JobProcess::job_status _status) { m_Status = _status; };
        inline void SetType(job_type _type) { m_Type = _type; };
        inline job_status GetStatus() { return m_Status; };
        inline job_type GetType() { return m_Type; };
        inline const char* JobProcessStatusToString();
        inline void SetProcessTime(uint32_t time){m_ProcessTime = time;};
        inline uint32_t GetProcessTime(){return m_ProcessTime;};
        inline void SetIndex(uint32_t index){m_Index = index;};
        inline uint32_t GetIndex(){return m_Index;};
        inline const char* JobProcessLocationToString();
//        inline void SetLocation(job_location _location){m_Location = _location;};
//        inline job_location GetLocation(){return m_Location;};
        inline void SetLocation(char* location) { m_location = location; };
        inline const char* GetLocation() { return m_location; };

        const char* ToString();

protected:
        AString m_Name;
        job_status m_Status;
        job_type m_Type;
        mutable uint32_t m_ProcessTime = 0;
        mutable uint32_t m_Index = 0 ;          // 过期成员，将在未来中移除
        mutable char* m_location;
        // job_location m_Location;
        
};

class JobProcessQueue
{
public:
        JobProcessQueue();
        ~JobProcessQueue();
        bool push(JobProcess *item);
        JobProcess* pop();
        Channel<JobProcess *> GetChannel(){return m_Queue;};
        bool empty(){ MutexHolder mh(m_Mutex); return m_Queue.empty();};
        size_t size(){return m_Queue.size();};

        uint32_t GetTotal() { MutexHolder mh(m_Mutex);  return total; };
        uint32_t GetSuccess() { MutexHolder mh(m_Mutex); return success; };
        uint32_t GetCache() { MutexHolder mh(m_Mutex); return cache;}
        uint32_t GetFailed() { MutexHolder mh(m_Mutex); return failed; };

private:
    Mutex m_Mutex;

protected:
        mutable uint32_t total = 0;
        mutable uint32_t success = 0;
        mutable uint32_t cache = 0;
        mutable uint32_t failed = 0;

        Channel<JobProcess *> m_Queue;
};