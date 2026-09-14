#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> xs) {
    long new_x = xs[0] - 1;
    xs.erase(xs.begin());
    while (new_x <= xs[0]) {
        xs.erase(xs.begin());
        new_x--;
    }
    xs.insert(xs.begin(), new_x);
    return xs;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)6, (long)3, (long)4, (long)1, (long)2, (long)3, (long)5}))) == (std::vector<long>({(long)5, (long)3, (long)4, (long)1, (long)2, (long)3, (long)5})));
}
