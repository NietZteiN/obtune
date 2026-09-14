#include<assert.h>
#include<bits/stdc++.h>

std::vector<long> f(std::vector<std::tuple<std::string, long>> parts) {
    std::unordered_map<std::string, long> dict;
    for (const auto& part : parts) {
        dict[std::get<0>(part)] = std::get<1>(part);
    }
    std::vector<long> values;
    for (const auto& part : parts) {
        if (dict.find(std::get<0>(part)) != dict.end()) {
            values.push_back(dict[std::get<0>(part)]);
            dict.erase(std::get<0>(part)); // Ensure each key is added only once
        }
    }
    return values;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::tuple<std::string, long>>({(std::tuple<std::string, long>)std::make_tuple("u", 1), (std::tuple<std::string, long>)std::make_tuple("s", 7), (std::tuple<std::string, long>)std::make_tuple("u", -5)}))) == (std::vector<long>({(long)-5, (long)7})));
}
