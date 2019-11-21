 
var map = new AMap.Map('container', {
    zoom:11,//级别
    center: [116.397428, 39.90923],//中心点坐标
    viewMode:'3D',//使用3D视图
    resizeEnable: true,
    zoomEnable: true,
});

function getLnglat(e) {
    var lnglat = e.lnglat;
    document.getElementById('lnglat').value = e.lnglat.toString()
    getArriveRange();
}
map.on( 'click', getLnglat);

var centerMarker;
function addCenterMarker(position){
    if(!centerMarker){
        centerMarker= new AMap.Marker({
            map: map,
            position: position
        });
    }else{
        centerMarker.setPosition(position)
    }
}


var arrivalRange,polygons=[];
//添加多边形覆盖物
function getArriveRange() {
    if(!arrivalRange){
        arrivalRange = new AMap.ArrivalRange()
    }
    var lnglat = $("#lnglat").val().split(',');
    var t = $("#t").val();
    var v = $("#v").val();
    
    addCenterMarker(lnglat);
    
    arrivalRange.search(lnglat, t, function(status,result){
        map.remove(polygons);
        polygons = [];
        if(result.bounds){
            for(var i=0;i<result.bounds.length;i++){
               var polygon = new AMap.Polygon({
                    fillColor:"#3366FF",
                    fillOpacity:"0.4",
                    strokeColor:"#00FF00",
                    strokeOpacity:"0.5",
                    strokeWeight:1
                });
                polygon.setPath(result.bounds[i]);
                polygons.push(polygon);
            }
            map.add(polygons);
            map.setFitView();
        }
    },{
        policy:v
    });
}


var isChanged=false;
$(function(){
    $('.single-slider').jRange({
        onstatechange: getArriveRange,
        from: 1,
        to: 120,
        step: 1,
        scale: [1,30,60,90,120],
        format: '%s',
        width: 400,
        showLabels: true,
        showScale: true
    });
});
getArriveRange();

$('#search').on('click', getArriveRange);
$('#v').on('change', getArriveRange);
$('#clear').on('click', function(){map.remove(polygons)});
