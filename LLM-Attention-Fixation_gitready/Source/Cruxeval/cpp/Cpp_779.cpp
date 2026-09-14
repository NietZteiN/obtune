#include<assert.h>
#include<bits/stdc++.h>

std::string f(std::string text) {
    std::istringstream iss(text);
    std::vector<std::string> tokens{std::istream_iterator<std::string>{iss}, std::istream_iterator<std::string>{}};
    std::string res = "${first}y, ${second}x, ${third}r, ${fourth}p";
    for (size_t i = 0; i < tokens.size(); ++i) {
        std::string placeholder = "${" + std::to_string(i + 1) + "}";
        size_t pos = res.find(placeholder);
        while (pos != std::string::npos) {
            res.replace(pos, placeholder.length(), tokens[i]);
            pos = res.find(placeholder, pos + tokens[i].length());
        }
    }
    return res;
}
int main() {
    auto candidate = f;
    assert(candidate(("python ruby c javascript")) == ("${first}y, ${second}x, ${third}r, ${fourth}p"));
}
