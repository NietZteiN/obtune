#include<assert.h>
#include<bits/stdc++.h>
union Union_std_string_std_vector_long_{
    std::string f0;
    std::vector<long> f1;
    Union_std_string_std_vector_long_(std::string _f0) : f0(_f0) {}
    Union_std_string_std_vector_long_(std::vector<long> _f1) : f1(_f1) {}
    ~Union_std_string_std_vector_long_() {}
    bool operator==(std::string f) {
        return f0 == f;
    }
    bool operator==(std::vector<long> f) {
        return f1 == f;
    }
};
Union_std_string_std_vector_long_ f(std::vector<long> array, long x, long i) {
    if (i < -(int)array.size() || i > (int)array.size() - 1) {
        return std::string("no");
    }
    array[i] = x;
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3, (long)4, (long)5, (long)6, (long)7, (long)8, (long)9, (long)10})), (11), (4)) == std::vector<long>({(long)1, (long)2, (long)3, (long)4, (long)11, (long)6, (long)7, (long)8, (long)9, (long)10}));
}
