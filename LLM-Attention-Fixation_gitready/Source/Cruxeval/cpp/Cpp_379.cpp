#include<assert.h>
#include<bits/stdc++.h>
union Union_bool_std_vector_long_{
    bool f0;
    std::vector<long> f1;    Union_bool_std_vector_long_(bool _f0) : f0(_f0) {}
    Union_bool_std_vector_long_(std::vector<long> _f1) : f1(_f1) {}
    ~Union_bool_std_vector_long_() {}
    bool operator==(bool f) {
        return f0 == f ;
    }    bool operator==(std::vector<long> f) {
        return f1 == f ;
    }
};
Union_bool_std_vector_long_ f(std::vector<long> nums) {
    for (int i = nums.size() - 1; i >= 0; i -= 3) {
        if (nums[i] == 0) {
            nums.clear();
            return Union_bool_std_vector_long_(false);
        }
    }
    return Union_bool_std_vector_long_(nums);
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)0, (long)0, (long)1, (long)2, (long)1}))) == false);
}
