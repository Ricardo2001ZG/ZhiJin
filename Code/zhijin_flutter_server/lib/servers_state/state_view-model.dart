
import 'package:dio/dio.dart';
import 'package:dio_http2_adapter/dio_http2_adapter.dart';
import 'package:flutter/foundation.dart';
import 'state_model.dart';

class ServersStateViewModel extends ValueNotifier<ServersStateModel>{
  String checkBaseUrl;
  int timeOutSec;
  Dio clientDio = Dio();

  ServersStateViewModel({
    required this.checkBaseUrl,
    this.timeOutSec = 10,
  }) : super(ServersStateModel()) {
    clientDio = Dio()
      ..options.baseUrl = checkBaseUrl
      ..interceptors.add(LogInterceptor())
      ..httpClientAdapter = HttpClientAdapter();
  }

  Future<bool> check(String uri) async {
    Response<String> response;
    try {
      response = await clientDio.get(uri);
      for (final e in response.redirects) {
        if (kDebugMode) {
          print('redirect: ${e.statusCode} ${e.location}');
        }
      }
      if (kDebugMode) {
        print(response.data);
      }
      return true;
    } catch (e) {
      if (kDebugMode) {
        print('远程服务器连接失败！');
      }
      return false;
    }
  }

  List getCheckStateList() {
    return value.checkStateList;
  }

  int getInitState() {
    return value.initState;
  }
}
