#include<assert.h>
#include<bits/stdc++.h>
union Union_std_vector_long__long{
    std::vector<long> f0;
    long f1;
    Union_std_vector_long__long(std::vector<long> _f0) : f0(_f0) {}
    Union_std_vector_long__long(long _f1) : f1(_f1) {}
    ~Union_std_vector_long__long() {}
    bool operator==(const std::vector<long>& f) const {
        return f0 == f;
    }
    bool operator==(const long& f) const {
        return f1 == f;
    }
};
Union_std_vector_long__long f(std::vector<std::vector<long>> ls, long n) {
    std::vector<long> answer;
    for (const auto& i : ls) {
        if (i[0] == n) {
            answer = i;
        }
    }
    return Union_std_vector_long__long(answer);
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::vector<long>>({(std::vector<long>)std::vector<long>({(long)1, (long)9, (long)4}), (std::vector<long>)std::vector<long>({(long)83, (long)0, (long)5}), (std::vector<long>)std::vector<long>({(long)9, (long)6, (long)100})})), (1)) == std::vector<long>({(long)1, (long)9, (long)4}));
}
