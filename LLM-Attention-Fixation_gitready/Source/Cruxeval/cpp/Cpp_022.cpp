#include<assert.h>
#include<bits/stdc++.h>
union Union_std_vector_long__long{
    std::vector<long> f0;
    long f1;    Union_std_vector_long__long(std::vector<long> _f0) : f0(_f0) {}
    Union_std_vector_long__long(long _f1) : f1(_f1) {}
    ~Union_std_vector_long__long() {}
    bool operator==(std::vector<long> f) {
        return f0 == f ;
    }    bool operator==(long f) {
        return f1 == f ;
    }
};
Union_std_vector_long__long f(long a) {
    if (a == 0) {
        return Union_std_vector_long__long(std::vector<long>{0});
    }
    std::vector<long> result;
    while (a > 0) {
        result.push_back(a % 10);
        a = a / 10;
    }
    std::reverse(result.begin(), result.end());
    std::string result_str;
    for (int i : result) {
        result_str += std::to_string(i);
    }
    return Union_std_vector_long__long(std::stol(result_str));
}
int main() {
    auto candidate = f;
    assert(candidate((0)) == std::vector<long>({(long)0}));
}
