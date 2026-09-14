#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string line, std::vector<std::tuple<std::string, std::string>> equalityMap) {
    std::map<char, char> rs;
    for (auto& k : equalityMap) {
        rs[std::get<0>(k)[0]] = std::get<1>(k)[0];
    }
    for (auto& c : line) {
        if (rs.count(c)) {
            c = rs[c];
        }
    }
    return line;
}
int main() {
    auto candidate = f;
    assert(candidate(("abab"), (std::vector<std::tuple<std::string, std::string>>({(std::tuple<std::string, std::string>)std::make_tuple("a", "b"), (std::tuple<std::string, std::string>)std::make_tuple("b", "a")}))) == ("baba"));
}
