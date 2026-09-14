#include<assert.h>
#include<bits/stdc++.h>
long f(std::map<long,std::vector<long>> d1, std::map<long,std::vector<long>> d2) {
    int mmax = 0;
    for (auto& pair : d1) {
        long k1 = pair.first;
        if (int p = pair.second.size() + d2[k1].size()) {
            if (p > mmax) {
                mmax = p;
            }
        }
    }
    return mmax;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,std::vector<long>>({{0, std::vector<long>()}, {1, std::vector<long>()}})), (std::map<long,std::vector<long>>({{0, std::vector<long>({(long)0, (long)0, (long)0, (long)0})}, {2, std::vector<long>({(long)2, (long)2, (long)2})}}))) == (4));
}
