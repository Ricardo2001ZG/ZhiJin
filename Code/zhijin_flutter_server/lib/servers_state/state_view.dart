
import 'package:flutter/material.dart';
import 'state_view-model.dart';

class _ServersStatePageState extends State<ServersStatePage> {
  final ServersStateViewModel _serversStateViewModel = ServersStateViewModel(
    checkBaseUrl: 'http://127.0.0.1:5000',
    timeOutSec: 10,
  );

  Future<List> generateStateList() async {
    return _serversStateViewModel.getCheckStateList();
  }

  Row getExpansionPanelNodeRow(int serviceState, String serviceName) {
    Color stateIconColor = Colors.yellow.shade700;
    Icon stateIcon = Icon(Icons.sync_problem, color: stateIconColor,);
    Text stateText = const Text(' - 未配置');
    if (serviceState == 1) {
      stateIconColor = Colors.green;
      stateText = const Text(' - 运行中');
      stateIcon = Icon(Icons.check_circle_outline, color: stateIconColor,);
    } else if (serviceState == 2) {
      stateIconColor = Colors.red;
      stateText = const Text(' - 未运行');
      stateIcon = Icon(Icons.cancel_outlined, color: stateIconColor,);
    } else if (serviceState == 3) {
      stateIconColor = Colors.grey;
      stateText = const Text(' - 检测中');
      stateIcon = Icon(Icons.sync_outlined, color: stateIconColor,);
      const stateLoading = CircularProgressIndicator();
      return Row(children: [
        Container(width: 25,),
        const SizedBox(width: 15, height: 15, child: stateLoading,),
        Container(width: 25,),
        Text(serviceName),
        stateText,
      ],);
    }
    return Row(children: [
      Container(width: 20,),
      stateIcon,
      Container(width: 20,),
      Text(serviceName),
      stateText,
    ],);
  }

  Widget _buildPanel() {
    return ExpansionPanelList(
      expansionCallback: (int index, bool isExpanded) {
        setState(() {
          _serversStateViewModel.getCheckStateList()[index]['isExpanded'] = !isExpanded;
        });
      },
      children: _serversStateViewModel.getCheckStateList().map<ExpansionPanel>((dynamic item) {
        if (!item.containsKey('isExpanded')) {
          item['isExpanded'] = false;
        }
        return ExpansionPanel(
          headerBuilder: (BuildContext context, bool isExpanded) {
            Row nodeRow = getExpansionPanelNodeRow(item['serviceState'], item['serviceName']);
            return nodeRow;
          },
          body: Column(children: [
            Container(height: 10,),
            Row(children: [
              Container(width: 20,),
              Text('检测服务： ${item['serviceUrlHost'] + item['serviceUri']}'),
              Expanded(child: Container(),),
              OutlinedButton(
                child: const Text('一键检测'),
                onPressed: () async {
                  setState(() {
                    item['serviceState'] = 3;
                  });
                  bool checkState = await _serversStateViewModel.check(item['serviceUri']);
                  setState(() {
                    if (checkState) {
                      item['serviceState'] = 1;
                    } else {
                      item['serviceState'] = 2;
                    }
                  });
                },
              ),
              Container(width: 20,),
            ],),
            Container(height: 10,),
            Row(children: [
              Container(width: 20,),
              Text('本地路径： ${item['servicePath']}'),
              Expanded(child: Container(),),
              const OutlinedButton(onPressed: null, child: Text('一键部署'),),
              Container(width: 20,),
            ],),
            Container(height: 10,),

            Container(height: 10,),
          ],),
          isExpanded: item['isExpanded'],
        );
      }).toList(),
    );
  }

  Widget stateListFutureBuilder() {
    if (_serversStateViewModel.getInitState() == -1) {
      return FutureBuilder(
        future: generateStateList(),
        builder: (BuildContext context, AsyncSnapshot snapshot) {
          switch (snapshot.connectionState) {
            case ConnectionState.none:
            case ConnectionState.waiting:
            case ConnectionState.active:
              return Center(
                child: Column(children: [
                  const SizedBox(
                    width: 15,
                    height: 15,
                    child: CircularProgressIndicator(),
                  ),
                  Container(height: 15,),
                  const Text('正在加载配置文件...'),
                ],),
              );
            case ConnectionState.done:
              return _buildPanel();
          }
        },
      );
    } else if (_serversStateViewModel.getInitState() == 2) {
      return const Center(child: Text('该功能在您的操作系统平台上未受支持，请联系开发人员。'),);
    }
    return _buildPanel();
  }

  @override
  Widget build(BuildContext context) {
    return Row(children: [
      Expanded(flex: 1, child: Container()),
      Expanded(
        flex: 3,
        child: SingleChildScrollView(
          child: stateListFutureBuilder(),
        ),
      ),
      Expanded(flex: 1, child: Container()),
    ],);
  }
}

class ServersStatePage extends StatefulWidget {
  const ServersStatePage({super.key});

  @override
  State<ServersStatePage> createState() => _ServersStatePageState();
}
