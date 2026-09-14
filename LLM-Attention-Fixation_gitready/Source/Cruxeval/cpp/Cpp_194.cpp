#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::vector<long>> f(std::vector<std::vector<long>> matr, long insert_loc) {
    matr.insert(matr.begin() + insert_loc, std::vector<long>{});
    return matr;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::vector<long>>({(std::vector<long>)std::vector<long>({(long)5, (long)6, (long)2, (long)3}), (std::vector<long>)std::vector<long>({(long)1, (long)9, (long)5, (long)6})})), (0)) == (std::vector<std::vector<long>>({(std::vector<long>)std::vector<long>(), (std::vector<long>)std::vector<long>({(long)5, (long)6, (long)2, (long)3}), (std::vector<long>)std::vector<long>({(long)1, (long)9, (long)5, (long)6})})));
}
