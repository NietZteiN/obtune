#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> lst) {
    auto operation = [](std::vector<long>& v) { std::reverse(v.begin(), v.end()); };
    std::vector<long> new_list = lst;
    std::sort(new_list.begin(), new_list.end());
    operation(new_list);
    return lst;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)6, (long)4, (long)2, (long)8, (long)15}))) == (std::vector<long>({(long)6, (long)4, (long)2, (long)8, (long)15})));
}
