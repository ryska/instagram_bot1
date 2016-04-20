<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="static/main.css">
    <link rel="stylesheet" type="text/css" href="static/materialize.css">
    <title>InstaBot</title>
</head>
<body>
% include('navbar.tpl')
<div class="container data-container">
    <div class="row">
        <div class="col s6">
            <div class="data-list">
                <p>Most popular hashtags on Instagram now:</p>
                   <ul class="hashtag-list">
                  % for item in tag_lists:
                    <li>#{{item}},</li>
                  % end
                   </ul>
            </div>
        </div>
        <div class="col s">
            <div class="data-sections">
              <table class="centered responsive-table">
                <thead>
                  <tr>
                      <th data-field="id">Posts:</th>
                      <th data-field="name">Following:</th>
                      <th data-field="price">Followers:</th>
                  </tr>
                </thead>

                <tbody>
                  <tr>
                    <td>{{posts}}</td>
                    <td>{{following}}</td>
                    <td>{{followed}}</td>
                  </tr>
                </tbody>
              </table>
            </div>
        </div>
    </div>
</div>
</body>
</html>