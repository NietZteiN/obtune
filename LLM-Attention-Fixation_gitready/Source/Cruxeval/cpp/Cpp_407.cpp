#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> s) {
    while (s.size() > 1) {
        s.clear();
        s.push_back(s.size());
    }
    int result = s.back();
    s.pop_back();
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)6, (long)1, (long)2, (long)3}))) == (0));
}
