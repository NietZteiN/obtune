#include<assert.h>
#include<bits/stdc++.h>
long f(std::map<long,long> d, long index) {
    long length = d.size();
    long idx = index % length;
    long v = d.rbegin()->second;
    for (long i = 0; i < idx; ++i) {
        d.erase(--d.end());
    }
    return v;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>({{27, 39}})), (1)) == (39));
}
