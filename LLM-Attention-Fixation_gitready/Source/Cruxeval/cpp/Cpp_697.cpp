#include<assert.h>
#include<bits/stdc++.h>
std::tuple<std::string, std::string, std::string> f(std::string s, std::string sep) {
    int sep_index = s.find(sep);
    std::string prefix = s.substr(0, sep_index);
    std::string middle = s.substr(sep_index, sep.length());
    std::string right_str = s.substr(sep_index + sep.length());
    return std::make_tuple(prefix, middle, right_str);
}
int main() {
    auto candidate = f;
    assert(candidate(("not it"), ("")) == (std::make_tuple("", "", "not it")));
}
