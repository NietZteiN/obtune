#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::map<long,long> d) {
    std::vector<long> result(d.size());
    long a = 0, b = 0;
    while(!d.empty()) {
        auto it = std::next(d.begin(), a == b);
        result[a] = it->first;
        d.erase(it);
        a = b;
        b = (b+1) % result.size();
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>())) == (std::vector<long>()));
}
