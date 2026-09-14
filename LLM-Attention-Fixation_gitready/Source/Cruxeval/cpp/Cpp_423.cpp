#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> selfie) {
    int lo = selfie.size();
    for(int i = lo-1; i >= 0; i--) {
        if(selfie[i] == selfie[0]) {
            selfie.erase(selfie.begin() + lo - 1);
        }
    }
    return selfie;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)4, (long)2, (long)5, (long)1, (long)3, (long)2, (long)6}))) == (std::vector<long>({(long)4, (long)2, (long)5, (long)1, (long)3, (long)2})));
}
