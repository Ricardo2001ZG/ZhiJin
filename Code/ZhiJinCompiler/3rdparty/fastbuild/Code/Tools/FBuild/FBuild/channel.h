// Queue - list of message
//--------------------------
#pragma once

// Includes
//------------------------------------------------------------------------------
#include "Core/Containers/Array.h"
#include "Core/Containers/Singleton.h"
#include "Core/Process/Mutex.h"
#include "Tools/FBuild/FBuildCore/FLog.h"

template <typename T>
class Channel
{
public:
    Channel(size_t cap = 4096)
    {
        m_Data = Array<T>(cap, true);
        m_Cost = cap;
    }

    ~Channel(); // 添加析构函数声明

    bool empty();
    size_t size();
    bool full();
    bool push(T &value);
    bool pop(T &value);

private:
    Mutex m_Mutex;
    Array<T> m_Data;
    size_t m_Cost{0};
};

template <typename T>
Channel<T>::~Channel() // 添加析构函数实现
{
    // 在这里清理类的资源，例如释放m_Data中的内存
    m_Data.Clear();
}

template <typename T>
bool Channel<T>::empty()
{
    return m_Data.IsEmpty();
}
template <typename T>

size_t Channel<T>::size()
{
    return m_Data.GetSize();
}
template <typename T>
bool Channel<T>::push(T &value)
{
    if (full())
    {
        return false;
    }
    MutexHolder mh(m_Mutex);
    m_Data.Append(value);
    return true;
}
template <typename T>
bool Channel<T>::pop(T &value)
{
    if (empty())
    {
        return false;
    }
    MutexHolder mh(m_Mutex);
    value = m_Data[0];
    m_Data.PopFront();
    return true;
}
template <typename T>
bool Channel<T>::full()
{
    return m_Data.GetSize() >= m_Cost;
}