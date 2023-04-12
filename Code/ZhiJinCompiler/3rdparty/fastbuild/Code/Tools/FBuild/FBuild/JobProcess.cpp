// -------------------------------
#pragma once

#include "Core/Strings/AString.h"
#include "Tools/FBuild/FBuild/JobProcess.h"
#include "Tools/FBuild/FBuild/channel.h"

JobProcess::JobProcess() {}

JobProcess::JobProcess(const AString name, job_status _status, job_type _type, uint32_t _index)
{
    SetName(AString(name.Get()));
    SetStatus(_status);
    SetType(_type);
    SetIndex(_index);
}
JobProcess::~JobProcess() {}

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

const char *JobProcess::JobProcessLocationToString()
{
    switch (GetLocation())
    {
    case JobProcess::job_location::local:
        return "local";
    case JobProcess::job_location::remote:
        return "remote";

    default:
        return "unknow";
    }
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
    if (item->GetType() == JobProcess::job_type::job)
    {
        total += 1;
        switch ((item->GetStatus()))
        {
        case JobProcess::job_status::cache:
        case JobProcess::job_status::success:
            success += 1;
            break;
        case JobProcess::job_status::failed:
            failed += 1;
            break;

        default:
            break;
        }
    }
    return m_Queue.push(item);
}

JobProcess* JobProcessQueue::pop()
{
    JobProcess *new_job = nullptr;
    bool result = m_Queue.pop(new_job);
    return new_job;
}