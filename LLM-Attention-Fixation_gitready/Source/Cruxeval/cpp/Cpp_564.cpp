#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<std::vector<long>> lists) {
    lists[1].clear();
    lists[2].insert(lists[2].end(), lists[1].begin(), lists[1].end());
    return lists[0];
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::vector<long>>({(std::vector<long>)std::vector<long>({(long)395, (long)666, (long)7, (long)4}), (std::vector<long>)std::vector<long>(), (std::vector<long>)std::vector<long>({(long)4223, (long)111})}))) == (std::vector<long>({(long)395, (long)666, (long)7, (long)4})));
}
