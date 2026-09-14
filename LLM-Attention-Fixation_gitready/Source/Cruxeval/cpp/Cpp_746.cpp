#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,std::string> f(std::map<std::string,std::string> dct) {
    std::map<std::string, std::string> result;
    std::vector<std::string> values;
    for (const auto& elem : dct) {
        values.push_back(elem.second);
    }
    for (const auto& value : values) {
        std::string item = value.substr(0, value.find('.')) + "@pinc.uk";
        result[value] = item;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,std::string>())) == (std::map<std::string,std::string>()));
}
