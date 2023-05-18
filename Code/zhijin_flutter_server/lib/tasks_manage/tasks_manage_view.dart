
import 'package:flutter/material.dart';
import 'package:graphic/graphic.dart';
import 'package:intl/intl.dart';
import '../tasks_manage/card_test_data.dart';

class TimeSeriesSales {
  final DateTime time;
  final int counts;

  TimeSeriesSales(this.time, this.counts);
}

class _TasksManagePageState extends State<TasksManagePage> {
  String innerPageRouterUrl = '/data_analysis';
  String innerPageTitle = '数据分析';

  Widget chartTestSmoothLine() {
    return Container(
      margin: const EdgeInsets.only(top: 10),
      width: 300,
      height: 250,
      child: Chart(
        data: invalidData,
        variables: {
          'Date': Variable(
            accessor: (Map map) => map['Date'] as String,
            scale: OrdinalScale(tickCount: 5),
          ),
          'Close': Variable(
            accessor: (Map map) =>
            (map['Close'] ?? double.nan) as num,
          ),
        },
        marks: [
          AreaMark(
            shape: ShapeEncode(value: BasicAreaShape(smooth: true)),
            color: ColorEncode(
                value: Defaults.colors10.first.withAlpha(80)),
          ),
          LineMark(
            shape: ShapeEncode(value: BasicLineShape(smooth: true)),
            size: SizeEncode(value: 0.5),
          ),
        ],
        axes: [
          Defaults.horizontalAxis,
          Defaults.verticalAxis,
        ],
        selections: {
          'touchMove': PointSelection(
            on: {
              GestureType.scaleUpdate,
              GestureType.tapDown,
              GestureType.longPressMoveUpdate
            },
            dim: Dim.x,
          )
        },
        tooltip: TooltipGuide(
          followPointer: [false, true],
          align: Alignment.topLeft,
          offset: const Offset(-20, -20),
        ),
        crosshair: CrosshairGuide(followPointer: [false, true]),
      ),
    );
  }

  Widget chartTestInteractiveBarChart() {
    return Chart(
      data: basicData,
      variables: {
        'genre': Variable(
          accessor: (Map map) => map['Platform'] as String,
        ),
        'sold': Variable(
          accessor: (Map map) => map['Usage'] as num,
        ),
      },
      marks: [
        IntervalMark(
          label: LabelEncode(
              encoder: (tuple) => Label(tuple['sold'].toString())),
          elevation: ElevationEncode(value: 0, updaters: {
            'tap': {true: (_) => 5}
          }),
          color:
          ColorEncode(value: Defaults.primaryColor, updaters: {
            'tap': {false: (color) => color.withAlpha(100)}
          }),
        )
      ],
      axes: [
        Defaults.horizontalAxis,
        Defaults.verticalAxis,
      ],
      selections: {'tap': PointSelection(dim: Dim.x)},
      tooltip: TooltipGuide(),
      crosshair: CrosshairGuide(),
    );
  }

  Widget testCard() {
    final monthDayFormat = DateFormat('MM-dd');
    final timeSeriesSales = [
      TimeSeriesSales(DateTime(2023, 9, 19), 5),
      TimeSeriesSales(DateTime(2023, 9, 26), 25),
      TimeSeriesSales(DateTime(2023, 10, 3), 100),
      TimeSeriesSales(DateTime(2023, 10, 10), 75),
    ];
    return Container(
      margin: const EdgeInsets.only(top: 10),
      width: 350,
      height: 350,
      child: Chart(
        data: timeSeriesSales,
        variables: {
          'time': Variable(
            accessor: (TimeSeriesSales datum) => datum.time,
            scale: TimeScale(
              formatter: (time) => monthDayFormat.format(time),
            ),
          ),
          'counts': Variable(
            accessor: (TimeSeriesSales datum) => datum.counts,
          ),
        },
        marks: [
          LineMark(
            shape: ShapeEncode(value: BasicLineShape(dash: [5, 2])),
            selected: {
              'touchMove': {1}
            },
          )
        ],
        coord: RectCoord(color: const Color(0xffdddddd)),
        axes: [
          Defaults.horizontalAxis,
          Defaults.verticalAxis,
        ],
        selections: {
          'touchMove': PointSelection(
            on: {
              GestureType.scaleUpdate,
              GestureType.tapDown,
              GestureType.longPressMoveUpdate
            },
            dim: Dim.x,
          )
        },
        tooltip: TooltipGuide(
          followPointer: [false, true],
          align: Alignment.topLeft,
          offset: const Offset(-20, -20),
        ),
        crosshair: CrosshairGuide(followPointer: [false, true]),
      ),
    );
  }

  Widget devCard(String cardTitle) {
    return Text('$cardTitle 页面开发中！');
  }

  Widget dataAnalysisCard(Widget chartWidget, String chartName) {
    return Card(
      clipBehavior: Clip.hardEdge,
      child: InkWell(
        onTap: () {},
        child: SizedBox(
          width: 350,
          height: 350,
          child: Center(child: SizedBox(
            width: 340,
            height: 340,
            child: Column(children: [
              Container(height: 10,),
              Expanded(child: Center(child: chartWidget,),),
              Container(height: 10,),
              Text(chartName),
              Container(height: 10,),
            ],),
          ),),
        ),
      ),
    );
  }

  Widget pageDataAnalysis() {
    return Column(children: [
      const SizedBox(height: 10,),
      Row(children: [
        const SizedBox(width: 15,),
        Text(
          innerPageTitle,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        Expanded(child: Container(),),
      ],),
      const SizedBox(height: 10,),
      const Divider(height: 1, color: Colors.black12,),
      Expanded(child: Center(child: Row(children: [
        Container(width: 30,),
        Expanded(child: Wrap(
          children: [
            dataAnalysisCard(chartTestSmoothLine(), '分布式编译时间统计'),
            dataAnalysisCard(chartTestInteractiveBarChart(), '编译机一小时内平均负载统计'),
            dataAnalysisCard(testCard(), '编译任务数量统计'),
            dataAnalysisCard(devCard(innerPageTitle), '敬请期待！'),
          ],
        ),),
        Container(width: 18,), // left : right = 1 : 0.618
      ],),),),
    ],);
  }

  Widget innerPageRouter() {
    switch (innerPageRouterUrl) {
      case '/compile_state':
        return Center(child: Text('$innerPageTitle 页面开发中，敬请期待！'),);
      case '/compile_configs':
        return Center(child: Text('$innerPageTitle 页面开发中，敬请期待！'),);
      case '/online_machine':
        return Center(child: Text('$innerPageTitle 页面开发中，敬请期待！'),);
      case '/data_analysis':
        return pageDataAnalysis();
    }
    return const Center(child: Text('404 Not Found，请联系开发人员！'),);
  }

  @override
  Widget build(BuildContext context) {
    List innerPageUrlList = [
      {
        'pageUrl': '/compile_state',
        'titleText': '编译状态',
        'pageIcon': Icons.format_list_numbered,
      },
      {
        'pageUrl': '/compile_configs',
        'titleText': '编译配置',
        'pageIcon': Icons.settings_applications_outlined,
      },
      {
        'pageUrl': '/online_machine',
        'titleText': '在线机器',
        'pageIcon': Icons.devices,
      },
      {
        'pageUrl': '/data_analysis',
        'titleText': '数据分析',
        'pageIcon': Icons.science_outlined,
      },
    ];
    return Row(children: [
      SizedBox(width: 200, child: ListView.builder(
          itemBuilder: (BuildContext context, int index) {
            if (index == 0) {
              return SizedBox(height: 70,child: Center(
                child: Text(
                  '分布式编译管理',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ),);
            }
            return ListTile(
              leading: Icon(innerPageUrlList[index - 1]['pageIcon']),
              title: Text(innerPageUrlList[index - 1]['titleText']),
              onTap: () {
                setState(() {
                  innerPageRouterUrl = innerPageUrlList[index - 1]['pageUrl'];
                  innerPageTitle = innerPageUrlList[index - 1]['titleText'];
                });
              },
            );
          },
          itemCount: innerPageUrlList.length + 1
      ),),
      const VerticalDivider(width: 1, color: Colors.black12,),
      Expanded(child: innerPageRouter(),),
    ],);
      // const );
  }
}

class TasksManagePage extends StatefulWidget {
  const TasksManagePage({super.key});

  @override
  State<TasksManagePage> createState() => _TasksManagePageState();
}
