#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> xs) {
    for (long i=-1, size=xs.size(); i>=-size; --i) {
        long val = xs[xs.size()+i];
        xs.push_back(val);
        xs.push_back(val);
    }
    return xs;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)4, (long)8, (long)8, (long)5}))) == (std::vector<long>({(long)4, (long)8, (long)8, (long)5, (long)5, (long)5, (long)5, (long)5, (long)5, (long)5, (long)5, (long)5})));
}
