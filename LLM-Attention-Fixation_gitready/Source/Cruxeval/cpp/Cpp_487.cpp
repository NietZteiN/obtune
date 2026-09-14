#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::map<long,std::string> dict) {
    std::vector<long> even_keys;
    for (auto const& pair : dict) {
        if (pair.first % 2 == 0) {
            even_keys.push_back(pair.first);
        }
    }
    return even_keys;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,std::string>({{4, "a"}}))) == (std::vector<long>({(long)4})));
}
