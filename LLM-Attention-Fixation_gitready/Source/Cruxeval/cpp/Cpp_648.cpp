#include<assert.h>
#include<bits/stdc++.h>
union Union_long_std_string{
    long f0;
    std::string f1;    Union_long_std_string(long _f0) : f0(_f0) {}
    Union_long_std_string(std::string _f1) : f1(_f1) {}
    ~Union_long_std_string() {}
    bool operator==(long f) {
        return f0 == f ;
    }    bool operator==(std::string f) {
        return f1 == f ;
    }
};
Union_long_std_string f(std::vector<long> list1, std::vector<long> list2) {
    std::vector<long> l = list1;
    while (l.size() > 0) {
        if (std::find(list2.begin(), list2.end(), l.back()) != list2.end()) {
            l.pop_back();
        } else {
            return l.back();
        }
    }
    return Union_long_std_string("missing");
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)0, (long)4, (long)5, (long)6})), (std::vector<long>({(long)13, (long)23, (long)-5, (long)0}))) == 6);
}
