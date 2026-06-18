package top.yogiczy.mytv.core.data.utils

import top.yogiczy.mytv.core.data.entities.channel.Channel
import top.yogiczy.mytv.core.data.entities.channel.ChannelLine
import top.yogiczy.mytv.core.data.entities.channel.ChannelLineList
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone


object ChannelUtil {
    private val hybridWebViewUrl by lazy {
        mapOf(
            ChannelAlias.standardChannelName("cctv-1") to listOf(
                "https://tv.cctv.com/live/cctv1/",
                "https://yangshipin.cn/tv/home?pid=600001859",
            ),
            ChannelAlias.standardChannelName("cctv-2") to listOf(
                "https://tv.cctv.com/live/cctv2/",
                "https://yangshipin.cn/tv/home?pid=600001800",
            ),
            ChannelAlias.standardChannelName("cctv-3") to listOf(
                "https://tv.cctv.com/live/cctv3/",
            ),
            ChannelAlias.standardChannelName("cctv-4") to listOf(
                "https://tv.cctv.com/live/cctv4/",
                "https://yangshipin.cn/tv/home?pid=600001814",
            ),
            ChannelAlias.standardChannelName("cctv-5") to listOf(
                "https://tv.cctv.com/live/cctv5/",
                "https://yangshipin.cn/tv/home?pid=600001818",
            ),
            ChannelAlias.standardChannelName("cctv-5+") to listOf(
                "https://tv.cctv.com/live/cctv5plus/",
                "https://yangshipin.cn/tv/home?pid=600001817",
            ),
            ChannelAlias.standardChannelName("cctv6") to listOf(
                "https://tv.cctv.com/live/cctv6/",
            ),
            ChannelAlias.standardChannelName("cctv-7") to listOf(
                "https://tv.cctv.com/live/cctv7/",
                "https://yangshipin.cn/tv/home?pid=600004092",
            ),
            ChannelAlias.standardChannelName("cctv-8") to listOf(
                "https://tv.cctv.com/live/cctv8/",
            ),
            ChannelAlias.standardChannelName("cctv-9") to listOf(
                "https://tv.cctv.com/live/cctvjilu/",
                "https://yangshipin.cn/tv/home?pid=600004078",
            ),
            ChannelAlias.standardChannelName("cctv-10") to listOf(
                "https://tv.cctv.com/live/cctv10/",
                "https://yangshipin.cn/tv/home?pid=600001805",
            ),
            ChannelAlias.standardChannelName("cctv-11") to listOf(
                "https://tv.cctv.com/live/cctv11/",
                "https://yangshipin.cn/tv/home?pid=600001806",
            ),
            ChannelAlias.standardChannelName("cctv-12") to listOf(
                "https://tv.cctv.com/live/cctv12/",
                "https://yangshipin.cn/tv/home?pid=600001807",
            ),
            ChannelAlias.standardChannelName("cctv-13") to listOf(
                "https://tv.cctv.com/live/cctv13/",
                "https://yangshipin.cn/tv/home?pid=600001811",
            ),
            ChannelAlias.standardChannelName("cctv-14") to listOf(
                "https://tv.cctv.com/live/cctvchild/",
                "https://yangshipin.cn/tv/home?pid=600001809",
            ),
            ChannelAlias.standardChannelName("cctv-15") to listOf(
                "https://tv.cctv.com/live/cctv15/",
                "https://yangshipin.cn/tv/home?pid=600001815",
            ),
            ChannelAlias.standardChannelName("cctv-16") to listOf(
                "https://tv.cctv.com/live/cctv16/",
                "https://yangshipin.cn/tv/home?pid=600098637",
            ),
            ChannelAlias.standardChannelName("cctv-17") to listOf(
                "https://tv.cctv.com/live/cctv17/",
            ),
            ChannelAlias.standardChannelName("北京卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002309",
            ),
            ChannelAlias.standardChannelName("江苏卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002521",
            ),
            ChannelAlias.standardChannelName("上海卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002483",
            ),
            ChannelAlias.standardChannelName("浙江卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002520",
            ),
            ChannelAlias.standardChannelName("湖南卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002475",
            ),
            ChannelAlias.standardChannelName("湖北卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002508",
            ),
            ChannelAlias.standardChannelName("广东卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002485",
            ),
            ChannelAlias.standardChannelName("广西卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002509",
            ),
            ChannelAlias.standardChannelName("黑龙江卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002498",
            ),
            ChannelAlias.standardChannelName("海南卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002506",
            ),
            ChannelAlias.standardChannelName("重庆卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002531",
            ),
            ChannelAlias.standardChannelName("深圳卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002481",
            ),
            ChannelAlias.standardChannelName("四川卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002516",
            ),
            ChannelAlias.standardChannelName("河南卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002525",
            ),
            ChannelAlias.standardChannelName("福建卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002484",
            ),
            ChannelAlias.standardChannelName("贵州卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002490",
            ),
            ChannelAlias.standardChannelName("江西卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002503",
            ),
            ChannelAlias.standardChannelName("辽宁卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002505",
            ),
            ChannelAlias.standardChannelName("安徽卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002532",
            ),
            ChannelAlias.standardChannelName("河北卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002493",
            ),
            ChannelAlias.standardChannelName("山东卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600002513",
            ),
            ChannelAlias.standardChannelName("天津卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600152137",
            ),
            ChannelAlias.standardChannelName("吉林卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600190405",
            ),
            ChannelAlias.standardChannelName("陕西卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600190400",
            ),
            ChannelAlias.standardChannelName("甘肃卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600190408",
            ),
            ChannelAlias.standardChannelName("宁夏卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600190737",
            ),
            ChannelAlias.standardChannelName("内蒙古卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600190401",
            ),
            ChannelAlias.standardChannelName("云南卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600190402",
            ),
            ChannelAlias.standardChannelName("山西卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600190407",
            ),
            ChannelAlias.standardChannelName("青海卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600190406",
            ),
            ChannelAlias.standardChannelName("西藏卫视") to listOf(
                "https://yangshipin.cn/tv/home?pid=600190403",
            ),
        )
    }

    fun getHybridWebViewLines(channelName: String): ChannelLineList {
        return ChannelLineList(hybridWebViewUrl[ChannelAlias.standardChannelName(channelName)]
            ?.map { ChannelLine(url = "webview://$it") }
            ?: emptyList())
    }

    fun getHybridWebViewUrlProvider(url: String): String {
        return if (url.contains("https://tv.cctv.com")) "央视网"
        else if (url.contains("https://yangshipin.cn")) "央视频"
        else "未知"
    }

    fun getPlaybackUrl(channel: Channel, line: ChannelLine, startTime: Long, endTime: Long): String? {
        // TVOD/PLTV
        if (listOf("pltv", "tvod").any { line.url.contains(it, ignoreCase = true) }) {
            var url = line.url.replace("pltv", "tvod", ignoreCase = true)
            if (url.contains("?")) {
                url += "&playseek=${startTime}-${endTime}"
            } else {
                url += "?playseek=${startTime}-${endTime}"
            }
            return url
        }

        if (channel.catchup == "default" && channel.catchupSource != null) {
            val source = channel.catchupSource

            // format: {utc:YmdHMS}
            if (source.contains("{utc:YmdHMS}")) {
                val sdf = SimpleDateFormat("yyyyMMddHHmmss", Locale.getDefault())
                sdf.timeZone = TimeZone.getTimeZone("UTC")
                val startTimeStr = sdf.format(Date(startTime * 1000))
                val endTimeStr = sdf.format(Date(endTime * 1000))

                return source
                    .replace("{utc:YmdHMS}", startTimeStr)
                    .replace("{utcend:YmdHMS}", endTimeStr)
            }

            // format: ${(b)yyyyMMddHHmmss|GMT}
            if (source.contains("\${(b)yyyyMMddHHmmss|GMT}")) {
                val sdf = SimpleDateFormat("yyyyMMddHHmmss", Locale.getDefault())
                sdf.timeZone = TimeZone.getTimeZone("GMT")
                val startTimeStr = sdf.format(Date(startTime * 1000))
                val endTimeStr = sdf.format(Date(endTime * 1000))
                return source
                    .replace("\${(b)yyyyMMddHHmmss|GMT}", startTimeStr)
                    .replace("\${(e)yyyyMMddHHmmss|GMT}", endTimeStr)
            }

            // format: {start|yyyyMMddHHmmss}
            if (source.contains("{start|yyyyMMddHHmmss}")) {
                val sdf = SimpleDateFormat("yyyyMMddHHmmss", Locale.getDefault())
                sdf.timeZone = TimeZone.getTimeZone("UTC")
                val startTimeStr = sdf.format(Date(startTime * 1000))
                val endTimeStr = sdf.format(Date(endTime * 1000))
                return source
                    .replace("{start|yyyyMMddHHmmss}", startTimeStr)
                    .replace("{end|yyyyMMddHHmmss}", endTimeStr)
            }

            // format: ${(b)yyyyMMddTHHmmss.00Z}
            if (source.contains("\${(b)yyyyMMddTHHmmss.00Z}")) {
                val sdf = SimpleDateFormat("yyyyMMdd'T'HHmmss'.00Z'", Locale.getDefault())
                sdf.timeZone = TimeZone.getTimeZone("UTC")
                val startTimeStr = sdf.format(Date(startTime * 1000))
                val endTimeStr = sdf.format(Date(endTime * 1000))
                return source
                    .replace("\${(b)yyyyMMddTHHmmss.00Z}", startTimeStr)
                    .replace("\${(e)yyyyMMddTHHmmss.00Z}", endTimeStr)
            }
        }

        return null
    }

    fun channelSupportPlayback(channel: Channel, line: ChannelLine): Boolean {
        return channel.catchup == "default" || listOf("pltv", "tvod").any { line.url.contains(it, ignoreCase = true) }
    }

    fun urlToCanPlayback(url: String): String {
        return url.replace("pltv", "tvod", ignoreCase = true)
    }
}
