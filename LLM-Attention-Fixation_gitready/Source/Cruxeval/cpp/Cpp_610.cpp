#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::vector<long> keys, long value) {
    std::map<long,long> d;
    for (long k : keys) {
        d[k] = value;
    }
    std::map<long,long> d_copy = d;
    for (long i = 1; i <= d_copy.size(); i++) {
        if (d.count(i) != 0 && d[i] == d_copy[i]) {
            d.erase(i);
        }
    }
    return d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)1, (long)1})), (3)) == (std::map<long,long>()));
}
