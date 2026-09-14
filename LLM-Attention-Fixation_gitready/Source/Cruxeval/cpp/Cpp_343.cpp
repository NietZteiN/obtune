#include<assert.h>
#include<bits/stdc++.h>

typedef std::variant<std::vector<long>, long> Union_std_vector_long__long;

std::vector<Union_std_vector_long__long> f(std::vector<Union_std_vector_long__long> array, std::vector<Union_std_vector_long__long> elem) {
    array.insert(array.end(), elem.begin(), elem.end());
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<Union_std_vector_long__long>({(std::vector<long>)std::vector<long>({(long)1, (long)2, (long)3}), (std::vector<long>)std::vector<long>({(long)1, (long)2}), (std::vector<long>)1})), (std::vector<Union_std_vector_long__long>({(std::vector<long>)std::vector<long>({(long)1, (long)2, (long)3}), (std::vector<long>)3, (std::vector<long>)std::vector<long>({(long)2, (long)1})}))) == (std::vector<Union_std_vector_long__long>({(std::vector<long>)std::vector<long>({(long)1, (long)2, (long)3}), (std::vector<long>)std::vector<long>({(long)1, (long)2}), (std::vector<long>)1, (std::vector<long>)std::vector<long>({(long)1, (long)2, (long)3}), (std::vector<long>)3, (std::vector<long>)std::vector<long>({(long)2, (long)1})})));
}
