#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> a) {
    std::vector<long> b = a;
    for(int k = 0; k < a.size() - 1; k += 2) {
        b.insert(b.begin() + k + 1, b[k]);
    }
    b.push_back(b[0]);
    return b;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)5, (long)5, (long)5, (long)6, (long)4, (long)9}))) == (std::vector<long>({(long)5, (long)5, (long)5, (long)5, (long)5, (long)5, (long)6, (long)4, (long)9, (long)5})));
}
