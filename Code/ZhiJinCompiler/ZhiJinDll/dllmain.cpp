// dllmain.cpp : 定义 DLL 应用程序的入口点。
#include "pch.h"

#define ZHIJINAPI extern "C" __declspec(dllexport) 

typedef void (*getCosFileFromRemote_func_t)(
    const char*, 
    const char*, 
    const char*
);

typedef int (*getBucketFromQcloudSdk_func_t) (
    int appId,
    std::string region,
    std::string bucket_name,
    std::string object_name,
    std::string local_path,
    std::string prefix,
    std::string token,
    std::string tmpSecretId,
    std::string tmpSecretKey
);

typedef int (*getObjectFromQcloudSdk_func_t) (
    int appId,
    std::string region,
    std::string bucket_name,
    std::string object_name,
    std::string local_path,
    std::string token,
    std::string tmpSecretId,
    std::string tmpSecretKey
);

getCosFileFromRemote_func_t getCosFileFromRemote_func = nullptr;
getBucketFromQcloudSdk_func_t getBucketFromQcloudSdk_func = nullptr;
getObjectFromQcloudSdk_func_t getObjectFromQcloudSdk_func = nullptr;

ZHIJINAPI int get_object_from_qcloud_sdk(
    int appId,
    const char* ffi_region,
    const char* ffi_bucket_name,
    const char* ffi_object_name,
    const char* ffi_local_path,
    const char* ffi_token,
    const char* ffi_tmpSecretId,
    const char* ffi_tmpSecretKey
) {
    std::string region(ffi_region);
    std::string bucket_name(ffi_bucket_name);
    std::string object_name(ffi_object_name);
    std::string local_path(ffi_local_path);
    std::string token(ffi_token);
    std::string tmpSecretId(ffi_tmpSecretId);
    std::string tmpSecretKey(ffi_tmpSecretKey);
    if (getObjectFromQcloudSdk_func != nullptr) {
        int resultCode = getObjectFromQcloudSdk_func(
            appId,
            region,
            bucket_name,
            object_name,
            local_path,
            token,
            tmpSecretId,
            tmpSecretKey
        );
        return resultCode;
    }
    return -1;
}

ZHIJINAPI int get_cos_file_from_remote(
    const char* ffi_token,
    const char* ffi_tmpSecretId, 
    const char* ffi_tmpSecretKey
) {
    std::string token(ffi_token);
    std::string tmpSecretId(ffi_tmpSecretId);
    std::string tmpSecretKey(ffi_tmpSecretKey);
    if (getCosFileFromRemote_func != nullptr) {
        getCosFileFromRemote_func(
            token.c_str(),
            tmpSecretId.c_str(),
            tmpSecretKey.c_str()
        );
        return 0;
    }
    return -1;
}

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    HMODULE qcloudSdkModule = nullptr;
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        SetDllDirectoryA("zhijin_library\\Debug");
        qcloudSdkModule = LoadLibraryA("qcloud_sdk.dll");
        if (qcloudSdkModule == nullptr) {
            std::cout << "Load qcloud_sdk.dll Failed!" << std::endl;
            char buf[255];
            GetCurrentDirectoryA(255, buf);
            std::string path(buf);
            std::cout << "Current Dir: " << path << std::endl;
        }
        else {
            getCosFileFromRemote_func = reinterpret_cast<getCosFileFromRemote_func_t>(
                GetProcAddress(qcloudSdkModule, "get_cos_file_from_remote")
                );
            getBucketFromQcloudSdk_func = reinterpret_cast<getBucketFromQcloudSdk_func_t>(
                GetProcAddress(qcloudSdkModule, "getBucket")
                );
            getObjectFromQcloudSdk_func = reinterpret_cast<getObjectFromQcloudSdk_func_t>(
                GetProcAddress(qcloudSdkModule, "multiGetObject")
                );
        }
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
