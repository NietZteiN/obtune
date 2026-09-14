#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::string text, std::string search_string) {
    std::vector<long> indexes;
    while (text.find(search_string) != std::string::npos) {
        indexes.push_back(text.rfind(search_string));
        text = text.substr(0, text.rfind(search_string));
    }
    return indexes;
}
int main() {
    auto candidate = f;
    assert(candidate(("ONBPICJOHRHDJOSNCPNJ9ONTHBQCJ"), ("J")) == (std::vector<long>({(long)28, (long)19, (long)12, (long)6})));
}
