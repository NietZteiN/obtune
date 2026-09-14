#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::tuple<std::string, long>> f(std::map<std::string,long> dct) {
    std::vector<std::tuple<std::string, long>> lst;
    for (const auto& pair : dct) {
        lst.push_back(std::make_tuple(pair.first, pair.second));
    }
    std::sort(lst.begin(), lst.end());
    return lst;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"a", 1}, {"b", 2}, {"c", 3}}))) == (std::vector<std::tuple<std::string, long>>({(std::tuple<std::string, long>)std::make_tuple("a", 1), (std::tuple<std::string, long>)std::make_tuple("b", 2), (std::tuple<std::string, long>)std::make_tuple("c", 3)})));
}
