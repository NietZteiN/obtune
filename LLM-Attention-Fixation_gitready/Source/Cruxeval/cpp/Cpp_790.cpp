#include<assert.h>
#include<bits/stdc++.h>
std::tuple<bool, bool> f(std::map<std::string,std::string> d) {
    std::map<std::string, std::map<std::string, std::string>> r = {
        {"c", d},
        {"d", d}
    };
    return std::make_tuple(false, r["c"] == r["d"]);
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,std::string>({{"i", "1"}, {"love", "parakeets"}}))) == (std::make_tuple(false, true)));
}
