/*
 * Copyright (c) 2017 Couchbase, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.couchbase.client.java.analytics;

import java.util.concurrent.TimeUnit;

import com.couchbase.client.core.annotations.InterfaceAudience;
import com.couchbase.client.core.annotations.InterfaceStability;
import com.couchbase.client.java.document.json.JsonArray;
import com.couchbase.client.java.document.json.JsonObject;
import rx.Observable;

@InterfaceStability.Committed
@InterfaceAudience.Public
public interface AsyncAnalyticsQueryResult {

    /**
     * @return an async stream of each row resulting from the query (empty if fatal errors occurred).
     */
    Observable<AsyncAnalyticsQueryRow> rows();

    /**
     * @return an async single-item representing the signature of the results, that can be used to
     * learn about the common structure of each {@link #rows() row}. This signature is usually a
     * {@link JsonObject}, but could also be any JSON-valid type like a boolean scalar, {@link JsonArray}...
     */
    Observable<Object> signature();

    /**
     * @return an async single item describing some metrics/info about the execution of the query.
     */
    Observable<AnalyticsMetrics> info();

    /**
     * Immediately denotes initial parsing success of the query.
     *
     * As rows are processed, it could be that a late failure occurs.
     * See {@link #finalSuccess} for the end of processing status.
     *
     * @return true if the query could be parsed, false if it short-circuited due to syntax/fatal error.
     */
    boolean parseSuccess();

    /**
     * Asynchronously returns the final status of the query. For example, a successful query will return
     * "<code>success</code>" (which is equivalent to {@link #finalSuccess()} returning true). Other statuses include
     * (but are not limited to) "<code>fatal</code>" when fatal errors occurred and "<code>timeout</code>" when the
     * query timed out on the server side but not yet on the client side. Receiving a (single) value for status means
     * the query is over.
     */
    Observable<String> status();

    /**
     * Asynchronously denotes the success or failure of the query. It could fail slower than with
     * {@link #parseSuccess()}, for example if a fatal error comes up while streaming the results
     * to the client. Receiving a (single) value for finalSuccess means the query is over.
     */
    Observable<Boolean> finalSuccess();

    /**
     * @return an async stream of errors or warnings encountered while executing the query.
     */
    Observable<JsonObject> errors();

    /**
     * @return the requestId generated by the server
     */
    String requestId();

    /**
     * @return the clientContextId that was set by the client (could be truncated to 64 bytes of UTF-8 chars)
     */
    String clientContextId();


    /** @return the {@link AsyncAnalyticsDeferredResultHandle} for deferred result fetch */
    @InterfaceStability.Experimental
    AsyncAnalyticsDeferredResultHandle handle();
}
