#include<assert.h>
#include<bits/stdc++.h>
union Union_std_string_std_vector_long_{
    std::string f0;
    std::vector<long> f1;    Union_std_string_std_vector_long_(std::string _f0) : f0(_f0) {}
    Union_std_string_std_vector_long_(std::vector<long> _f1) : f1(_f1) {}
    ~Union_std_string_std_vector_long_() {}
    bool operator==(std::string f) {
        return f0 == f ;
    }    bool operator==(std::vector<long> f) {
        return f1 == f ;
    }
};
Union_std_string_std_vector_long_ f(std::vector<long> first, std::vector<long> second) {
    if(first.size() < 10 || second.size() < 10) {
        return Union_std_string_std_vector_long_("no");
    }
    for(int i = 0; i < 5; i++) {
        if(first[i] != second[i]) {
            return Union_std_string_std_vector_long_("no");
        }
    }
    first.insert(first.end(), second.begin(), second.end());
    return Union_std_string_std_vector_long_(first);
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)1})), (std::vector<long>({(long)1, (long)1, (long)2}))) == "no");
}
