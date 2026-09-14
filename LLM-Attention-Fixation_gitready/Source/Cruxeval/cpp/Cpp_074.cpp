#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> lst, long i, long n) {
    lst.insert(lst.begin() + i, n);
    return lst;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)44, (long)34, (long)23, (long)82, (long)24, (long)11, (long)63, (long)99})), (4), (15)) == (std::vector<long>({(long)44, (long)34, (long)23, (long)82, (long)15, (long)24, (long)11, (long)63, (long)99})));
}
