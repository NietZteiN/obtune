#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string sep, long maxsplit) {
    std::vector<std::string> splitted;
    size_t pos = 0;
    size_t found;
    while ((found = text.find(sep, pos)) != std::string::npos && maxsplit > 0) {
        splitted.push_back(text.substr(pos, found - pos));
        pos = found + sep.size();
        maxsplit--;
    }
    splitted.push_back(text.substr(pos));

    size_t length = splitted.size();
    std::vector<std::string> new_splitted(splitted.begin(), splitted.begin() + length / 2);
    std::reverse(new_splitted.begin(), new_splitted.end());
    new_splitted.insert(new_splitted.end(), splitted.begin() + length / 2, splitted.end());

    return std::accumulate(new_splitted.begin(), new_splitted.end(), std::string(), [&](const std::string &a, const std::string &b) {
        return a.empty() ? b : a + sep + b;
    });
}
int main() {
    auto candidate = f;
    assert(candidate(("ertubwi"), ("p"), (5)) == ("ertubwi"));
}
