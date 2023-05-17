// -------------------------------
#pragma once

#include "Core/Strings/AString.h"
#include "Tools/FBuild/FBuild/JobProcess.h"
#include "Tools/FBuild/FBuild/channel.h"

JobProcess::JobProcess() {
    this->SetStatus(job_status::process);
}

JobProcess::JobProcess(const AString name, job_status _status, job_type _type, uint32_t _index)
{
    SetName(AString(name.Get()));
    SetStatus(_status);
    SetType(_type);
    SetIndex(_index);
}
JobProcess::~JobProcess() {
    // delete m_location;
}

const char *JobProcess::JobProcessStatusToString()
{
    switch (GetStatus())
    {
    case JobProcess::job_status::process:
        return "process";
    case JobProcess::job_status::success:
        return "success";
    case JobProcess::job_status::failed:
        return "failed";
    case JobProcess::job_status::cache:
        return "cache";
    default:
        return "unknown";
    }
}


// 遗弃方法，将在未来移除
const char *JobProcess::JobProcessLocationToString()
{
    /*
    switch (GetLocation())
    {
    case JobProcess::job_location::local:
        return "local";
    case JobProcess::job_location::remote:
        return "remote";

    default:
        return "unknow";
    }
    */
    return GetLocation();
}


const char* JobProcess::ToString() {
    AStackString<4096> message;
    message.AppendFormat("job_name '%s' stats %s location %s buildTime %u",
        this->GetName(),
        this->JobProcessStatusToString(),
        this->GetLocation(),
        this->GetProcessTime());
    return message.Get();
}


JobProcessQueue::JobProcessQueue()
{
    m_Queue = Channel<JobProcess *>(4096);
    total = 0;
    success = 0;
    failed = 0;
}

JobProcessQueue::~JobProcessQueue()
{
    if (m_Queue.empty())
    {
        m_Queue.~Channel();
    }
}

bool JobProcessQueue::push(JobProcess *item)
{
    if (item == nullptr)
    {
        return false;
    }

    // 加锁避免多线程下计量数值不对
    m_Mutex.Lock();
    if (item->GetType() == JobProcess::job_type::job)
    {
        switch ((item->GetStatus()))
        {
        case JobProcess::job_status::cache:
            cache += 1;
            break;
        case JobProcess::job_status::success:
            success += 1;
            break;
        case JobProcess::job_status::failed:
            failed += 1;
            break;
        case JobProcess::job_status::process:
            total += 1;
            break;
        default:
            break;
        }
    }
    m_Mutex.Unlock();
    return m_Queue.push(item);
}

JobProcess* JobProcessQueue::pop()
{
    JobProcess *new_job = nullptr;
    m_Queue.pop(new_job);
    return new_job;
}
