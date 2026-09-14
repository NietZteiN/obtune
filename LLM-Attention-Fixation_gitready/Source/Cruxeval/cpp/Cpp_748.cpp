#include<assert.h>
#include<bits/stdc++.h>
std::tuple<std::tuple<std::string, long>, std::tuple<std::string, long>> f(std::map<std::string,long> d) {
    auto it = d.begin();
    std::tuple<std::string, long> first = std::make_tuple(it->first, it->second);
    ++it;
    std::tuple<std::string, long> second = std::make_tuple(it->first, it->second);
    return std::make_tuple(first, second);
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"a", 123}, {"b", 456}, {"c", 789}}))) == (std::make_tuple(std::make_tuple("a", 123), std::make_tuple("b", 456))));
}
