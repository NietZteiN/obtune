#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> arr) {
    std::vector<long> n;
    for (long item : arr) {
        if (item % 2 == 0) {
            n.push_back(item);
        }
    }

    std::vector<long> m;
    m.insert(m.end(), n.begin(), n.end());
    m.insert(m.end(), arr.begin(), arr.end());

    for (auto it = m.begin(); it != m.end();) {
        if (std::find(n.begin(), n.end(), *it) == n.end()) {
            it = m.erase(it);
        } else {
            ++it;
        }
    }

    return m;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)3, (long)6, (long)4, (long)-2, (long)5}))) == (std::vector<long>({(long)6, (long)4, (long)-2, (long)6, (long)4, (long)-2})));
}
