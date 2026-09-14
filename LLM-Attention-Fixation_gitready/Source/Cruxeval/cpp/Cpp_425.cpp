#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string a) {
    a = std::regex_replace(a, std::regex("/"), ":");
    std::string x, y, z;
    std::tie(x, y, z) = std::make_tuple(a.substr(0, a.find_last_of(":")), ":", a.substr(a.find_last_of(":") + 1));
    return {x, y, z};
}
int main() {
    auto candidate = f;
    assert(candidate(("/CL44     ")) == (std::vector<std::string>({(std::string)"", (std::string)":", (std::string)"CL44     "})));
}
