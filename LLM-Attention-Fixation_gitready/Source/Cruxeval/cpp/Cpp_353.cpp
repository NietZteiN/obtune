#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> x) {
    if (x.size() == 0) {
        return -1;
    } else {
        std::unordered_map<long, int> cache;
        for (long item : x) {
            if (cache.find(item) != cache.end()) {
                cache[item] += 1;
            } else {
                cache[item] = 1;
            }
        }
        int max_count = 0;
        for (const auto& pair : cache) {
            max_count = std::max(max_count, pair.second);
        }
        return max_count;
    }
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)0, (long)2, (long)2, (long)0, (long)0, (long)0, (long)1}))) == (4));
}
