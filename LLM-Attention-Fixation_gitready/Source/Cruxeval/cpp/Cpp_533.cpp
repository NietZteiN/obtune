#include<assert.h>
#include<bits/stdc++.h>
long f(std::string query, std::map<std::string,long> base) {
    long net_sum = 0;
    for (auto const& pair : base) {
        std::string key = pair.first;
        long val = pair.second;
        if (key[0] == query[0] && key.size() == 3) {
            net_sum -= val;
        } else if (key[key.size() - 1] == query[0] && key.size() == 3) {
            net_sum += val;
        }
    }
    return net_sum;
}
int main() {
    auto candidate = f;
    assert(candidate(("a"), (std::map<std::string,long>())) == (0));
}
