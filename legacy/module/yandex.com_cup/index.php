<?php
    require_once dirname(__FILE__) . "/../../config.php";


    $url = $URL;

    $page = curlexec($url);
    preg_match('#<meta[^>]*name="next-head-count"[^>]*content="(?P<year>[0-9]+)"[^>]*>#', $page, $match);
    $year = $match['year'];
    if (strlen($year) < 4) {
        $y = date('Y');
        $year = substr($y, 0, 4 - strlen($year)) . $year;
    }

    preg_match_all('#<a[^>]*home-hero__link[^>]*home-hero__link_(?P<type>[a-z]+)[^>]*href="(?P<href>[^"]*)"[^>]*>.*?<[^>]*home-hero__title[^>]*>(?P<name>[^<]*)(</[^>]*>)*</a>#', $page, $matches, PREG_SET_ORDER);

    foreach ($matches as $category) {
        $url = url_merge($URL, $category['href']);
        $page = curlexec($url);

        preg_match_all('#<[^>]*home-stages__date[^>]*>(?<date>[^<]*)<[^>]*>\s*<[^>]*home-stages__title[^>]*>(?<title>[^<]*)<[^>]*>#', $page, $matches, PREG_SET_ORDER);
        foreach ($matches as $stage) {
            $sep = '–';
            $start_time = $stage['date'];
            $start_time = preg_replace("#[^0-9a-z$sep]+#i", " ", $start_time);
            $start_time = preg_replace("#\s*$sep\s*#i", $sep, $start_time);
            if (strpos($start_time, $sep) !== false) {
                list($start_time, $end_time) = explode($sep, $start_time);
                $start_time = trim($start_time);
                $end_time = trim($end_time);
                if (preg_match('#^[0-9]+$#', $end_time)) {
                    $end_time = preg_replace('#[0-9]+#', $end_time, $start_time);
                }
            } else {
                $end_time = $start_time;
            }
            if (strpos($start_time, $year) === false) {
                $start_time .= " $year";
            }
            if (strpos($end_time, $year) === false) {
                $end_time .= " $year";
            }

            $month = date('n', strtotime($start_time));
            if ($month >= 9) {
                $season = ($year + 0) . "-" . ($year + 1);
            } else {
                $season = ($year - 1) . "-" . ($year + 0);
            }

            $title = $category['name'] . '. ' . $stage['title'];
            $key = $category['type'] . ' ' . strtolower($stage['title']) . ' ' . $season;

            $contests[] = array(
                'start_time' => $start_time,
                'end_time' => strtotime($end_time) + 24 * 60 * 60,  # + day
                'title' => $title,
                'url' => $url,
                'host' => $HOST,
                'rid' => $RID,
                'timezone' => $TIMEZONE,
                'key' => $key,
            );
        }
    }

    if ($RID == -1) {
        print_r($contests);
    }
?>
