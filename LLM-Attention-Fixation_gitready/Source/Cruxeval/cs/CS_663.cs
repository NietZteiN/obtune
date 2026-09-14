using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> container, long cron) {
        if (!container.Contains(cron))
            return container;
        List<long> pref = container.GetRange(0, container.IndexOf(cron));
        List<long> suff = container.GetRange(container.IndexOf(cron) + 1, container.Count - container.IndexOf(cron) - 1);
        return pref.Concat(suff).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>()), (2L)).SequenceEqual((new List<long>())));
    }

}
