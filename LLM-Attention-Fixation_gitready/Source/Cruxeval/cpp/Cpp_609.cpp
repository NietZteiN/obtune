#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> array, long elem) {
    std::map<long,long> result = array;
    while (!result.empty()) {
        auto it = result.end();
        --it;
        if (it->first == elem || it->second == elem) {
            result.insert(array.begin(), array.end());
        }
        result.erase(it->first);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>()), (1)) == (std::map<long,long>()));
}
