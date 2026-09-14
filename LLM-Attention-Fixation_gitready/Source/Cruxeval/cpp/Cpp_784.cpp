#include<assert.h>
#include<bits/stdc++.h>
std::tuple<std::string, std::string> f(std::string key, std::string value) {
    std::map<std::string, std::string> dict_ = {{key, value}};
    std::tuple<std::string, std::string> result = *dict_.begin();
    dict_.erase(dict_.begin());
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("read"), ("Is")) == (std::make_tuple("read", "Is")));
}
