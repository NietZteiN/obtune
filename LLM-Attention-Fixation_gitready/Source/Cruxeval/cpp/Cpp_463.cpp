#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> dict) {
    std::map<long, long> result = dict;
    std::vector<long> remove_keys;
    for (auto& pair : dict) {
        if (dict.find(pair.second) != dict.end()) {
            remove_keys.push_back(pair.first);
        }
    }
    for (auto key : remove_keys) {
        result.erase(key);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>({{-1, -1}, {5, 5}, {3, 6}, {-4, -4}}))) == (std::map<long,long>({{3, 6}})));
}
