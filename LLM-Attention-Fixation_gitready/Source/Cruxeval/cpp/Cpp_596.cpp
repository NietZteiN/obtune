#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> txt, std::string alpha) {
    std::sort(txt.begin(), txt.end());
    if (std::distance(txt.begin(), std::find(txt.begin(), txt.end(), alpha)) % 2 == 0) {
        std::reverse(txt.begin(), txt.end());
    }
    return txt;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"8", (std::string)"9", (std::string)"7", (std::string)"4", (std::string)"3", (std::string)"2"})), ("9")) == (std::vector<std::string>({(std::string)"2", (std::string)"3", (std::string)"4", (std::string)"7", (std::string)"8", (std::string)"9"})));
}
