#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> d, long n) {
    for(int i=0; i<n; i++) {
        auto item = *d.rbegin();
        d.erase(item.first);
        d[item.second] = item.first;
    }
    return d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>({{1, 2}, {3, 4}, {5, 6}, {7, 8}, {9, 10}})), (1)) == (std::map<long,long>({{1, 2}, {3, 4}, {5, 6}, {7, 8}, {10, 9}})));
}
